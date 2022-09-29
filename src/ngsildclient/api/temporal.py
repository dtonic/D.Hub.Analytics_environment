#!/usr/bin/env python3

# Software Name: ngsildclient
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

from __future__ import annotations
from typing import TYPE_CHECKING, Union, List, Optional, Generator, Callable
from dataclasses import dataclass
from datetime import timedelta
from isodate import duration_isoformat
from ngsildclient.utils import iso8601

import logging
import operator

if TYPE_CHECKING:
    from .client import Client

from .constants import EntityId, JSONLD_CONTEXT, AggrMethod
from .helper.temporal import TemporalQuery
from ..model.entity import Entity


logger = logging.getLogger(__name__)


def addopt(params: dict, newopt: str):
    if params.get("options", "") == "":
        params["options"] = newopt
    else:
        params["options"] += f",{newopt}"


def troes_to_dict(troes: dict):
    d = {}
    if not isinstance(troes, List):
        troes = [troes]
    troe: dict = troes[0]
    attrs = [str(k) for k in troe.keys() if k not in ("id", "type", "@context")]
    attr0 = attrs[0]
    n = len(troe[attr0])
    datetimes = [x[1] for x in troe[attr0]["values"]]
    if len(attrs) > 1:
        for attr in attrs[1:]:
            if [x[1] for x in troe[attr]["values"]] != datetimes:
                raise ValueError("Cannot pack result : attributes have distinct observedAt values.")
    etype = troe["type"]
    d[etype] = operator.iconcat(*[[troe["id"].rsplit(":")[-1]] * n for troe in troes])
    d["observed"] = [iso8601.parse(x)[2] for x in datetimes] * n
    for attr in attrs:
        d[attr] = []
        for troe in troes:
            for value in troe[attr]["values"]:
                d[attr].append(value[0])
    return d


@dataclass
class Pagination:
    count: int = 0
    pagesize: int = 0
    next_url: Optional[str] = None
    prev_url: Optional[str] = None

    @classmethod
    def from_headers(cls, headers: dict):
        count = int(headers.get("NGSILD-Results-Count", 0))
        pagesize = int(headers.get("Page-Size", 0))
        next_url = headers.get("Next-Page")
        prev_url = headers.get("Previous-Page")
        return cls(count, pagesize, next_url, prev_url)


@dataclass
class TemporalResult:
    result: List[dict]
    pagination: Optional[Pagination] = None


class Temporal:
    def __init__(self, client: Client, url: str):
        self._client = client
        self._session = client.session
        self.url = url

    def _get(
        self,
        eid: Union[EntityId, Entity],
        attrs: List[str] = None,
        ctx: str = None,
        verbose: bool = False,
        lastn: int = 0,
        pagesize: int = 0,  # default broker pageSize
        pageanchor: str = None,
        count: bool = True,
    ) -> TemporalResult:
        eid = eid.id if isinstance(eid, Entity) else eid
        params = {}
        headers = {
            "Accept": "application/ld+json",
            "Content-Type": None,
        }  # overrides session headers
        if ctx is not None:
            headers["Link"] = f'<{ctx}>; rel="{JSONLD_CONTEXT}"; type="application/ld+json"'
        if count:
            addopt(params, "count")
        params = {}
        if attrs:
            params["attrs"] = ",".join(attrs)
        if lastn > 0:
            params["lastN"] = lastn
        if pagesize > 0:
            params["pageSize"] = pagesize
        if pageanchor is not None:
            params["pageAnchor"] = pageanchor
        if not verbose:
            addopt(params, "temporalValues")
        r = self._session.get(f"{self.url}/{eid}", headers=headers, params=params)
        self._client.raise_for_status(r)
        return TemporalResult(r.json(), Pagination.from_headers(r.headers))

    #  equivalent to get_all()
    def get(
        self,
        eid: Union[EntityId, Entity],
        attrs: List[str] = None,
        ctx: str = None,
        verbose: bool = False,
        pagesize: int = 0,
        packed: bool = False,
    ) -> List[dict]:
        verbose = False if packed else verbose
        r: TemporalResult = self._get(eid, attrs, ctx, verbose, pagesize=pagesize)
        troes: List[dict] = r.result
        while r.pagination.next_url is not None:
            r: TemporalResult = self._get(eid, attrs, ctx, verbose, pagesize=pagesize, pageanchor=r.pagination.next_url)
            troes.extend(r.result)
        return troes_to_dict(troes) if packed else troes

    def _query(
        self,
        eid: Union[EntityId, Entity] = None,
        type: str = None,
        attrs: List[str] = None,
        q: str = None,
        gq: str = None,
        ctx: str = None,
        verbose: bool = False,
        tq: TemporalQuery = None,
        lastn: int = 0,
        pagesize: int = 0,  # default broker pageSize
        pageanchor: str = None,
        count: bool = True,
    ) -> TemporalResult:
        params = {}
        if eid:
            params["id"] = eid
        if type:
            params["type"] = type
        if attrs:
            params["attrs"] = ",".join(attrs)
        if q:
            params["q"] = q
        if gq:
            params["georel"] = gq
        if count:
            addopt(params, "count")
        if not verbose:
            addopt(params, "temporalValues")
        if tq is None:
            tq = TemporalQuery().before()
        params |= tq
        if lastn > 0:
            params["lastN"] = lastn
        if pagesize > 0:
            params["pageSize"] = pagesize
        if pageanchor is not None:
            params["pageAnchor"] = pageanchor
        headers = {
            "Accept": "application/ld+json",
            "Content-Type": None,
        }  # overrides session headers
        if ctx is not None:
            headers["Link"] = f'<{ctx}>; rel="{JSONLD_CONTEXT}"; type="application/ld+json"'
        r = self._session.get(
            self.url,
            headers=headers,
            params=params,
        )
        self._client.raise_for_status(r)
        return TemporalResult(r.json(), Pagination.from_headers(r.headers))

    def query_head(
        self,
        *,
        eid: Union[EntityId, Entity] = None,
        type: str = None,
        attrs: List[str] = None,
        q: str = None,
        gq: str = None,
        ctx: str = None,
        verbose: bool = False,
        tq: TemporalQuery = None,
        limit: int = 5,
        packed: bool = False,
    ) -> List[dict]:
        verbose = False if packed else verbose
        troes = self._query(eid, type, attrs, q, gq, ctx, verbose, tq, lastn=limit, pagesize=limit).result
        return troes_to_dict(troes) if packed else troes

    def query_all(
        self,
        *,
        eid: Union[EntityId, Entity] = None,
        type: str = None,
        attrs: List[str] = None,
        q: str = None,
        gq: str = None,
        ctx: str = None,
        verbose: bool = False,
        tq: TemporalQuery = None,
        pagesize: int = 0,
        packed: bool = False,
    ) -> List[dict]:
        verbose = False if packed else verbose
        r: TemporalResult = self._query(eid, type, attrs, q, gq, ctx, verbose, tq, pagesize=pagesize)
        troes: List[dict] = r.result
        while r.pagination.next_url is not None:
            r: TemporalResult = self._query(
                eid, type, attrs, q, gq, ctx, verbose, tq, pagesize=pagesize, pageanchor=r.pagination.next_url
            )
            troes.extend(r.result)
        return troes_to_dict(troes) if packed else troes

    def query_generator(
        self,
        *,
        eid: Union[EntityId, Entity] = None,
        type: str = None,
        attrs: List[str] = None,
        q: str = None,
        gq: str = None,
        ctx: str = None,
        verbose: bool = False,
        tq: TemporalQuery = None,
        pagesize: int = 0,
    ) -> Generator[List[dict], None, None]:
        r: TemporalResult = self._query(eid, type, attrs, q, gq, ctx, verbose, tq, pagesize=pagesize)
        troes = r.result
        yield from troes
        while r.pagination.next_url is not None:
            r: TemporalResult = self._query(
                eid, type, attrs, q, gq, ctx, verbose, tq, pagesize=pagesize, pageanchor=r.pagination.next_url
            )
            troes = r.result
            yield from troes

    def query_handle(
        self,
        *,
        eid: Union[EntityId, Entity] = None,
        type: str = None,
        attrs: List[str] = None,
        q: str = None,
        gq: str = None,
        ctx: str = None,
        verbose: bool = False,
        tq: TemporalQuery = None,
        pagesize: int = 0,
        packed: bool = False,
        callback: Callable[[Entity], None],
    ) -> None:
        for troe in self.query_generator(eid, type, attrs, q, gq, ctx, verbose, tq, pagesize, packed):
            callback(troe)

    def aggregate(
        self,
        *,
        type: str = None,
        attrs: List[str] = None,
        q: str = None,
        gq: str = None,
        ctx: str = None,
        tq: TemporalQuery = None,
        lastn: int = 0,
        pagesize: int = 0,  # default broker pageSize
        pageanchor: str = None,
        count: bool = False,
        methods: List[AggrMethod] = [AggrMethod.AVERAGE],
        period: timedelta = timedelta(days=1),
    ) -> TemporalResult:
        params = {}
        if type:
            params["type"] = type
        if attrs:
            params["attrs"] = ",".join(attrs)
        if q:
            params["q"] = q
        if gq:
            params["georel"] = gq
        addopt(params, "aggregatedValues")
        if count:
            addopt(params, "count")
        if tq is None:
            tq = TemporalQuery().before()
        params |= tq
        if lastn > 0:
            params["lastN"] = lastn
        if pagesize > 0:
            params["pageSize"] = pagesize
        if pageanchor is not None:
            params["pageAnchor"] = pageanchor
        params["aggrMethods"] = ",".join([m.value for m in methods])
        params["aggrPeriodDuration"] = duration_isoformat(period)
        headers = {
            "Accept": "application/ld+json",
            "Content-Type": None,
        }  # overrides session headers
        if ctx is not None:
            headers["Link"] = f'<{ctx}>; rel="{JSONLD_CONTEXT}"; type="application/ld+json"'
        r = self._session.get(
            self.url,
            headers=headers,
            params=params,
        )
        self._client.raise_for_status(r)
        return TemporalResult(r.json(), Pagination.from_headers(r.headers))
