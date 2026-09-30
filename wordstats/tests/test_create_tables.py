# -*- coding: utf8 -*-
import multiprocessing
import os
import tempfile
from unittest import TestCase

from sqlalchemy import create_engine, inspect

from wordstats.base_service import create_tables

PROCESSES = 8
ROUNDS = 10


def _create(path, barrier, results):
    engine = create_engine('sqlite:///' + path)
    barrier.wait()
    try:
        create_tables(engine)
        results.put(None)
    except Exception as e:
        results.put(repr(e))


class CreateTablesTests(TestCase):

    def test_concurrent_processes_all_succeed(self):
        # gunicorn workers booting on a fresh container import wordstats at
        # the same time; without the retry most of them failed with
        # "table word_info already exists" and took the container down
        ctx = multiprocessing.get_context('fork')
        with tempfile.TemporaryDirectory() as folder:
            for i in range(ROUNDS):
                path = os.path.join(folder, f'race-{i}.db')
                barrier = ctx.Barrier(PROCESSES, timeout=30)
                results = ctx.Queue()
                processes = [ctx.Process(target=_create, args=(path, barrier, results))
                             for _ in range(PROCESSES)]
                for p in processes:
                    p.start()
                errors = [e for e in (results.get(timeout=60) for _ in processes) if e]
                for p in processes:
                    p.join()

                self.assertEqual([], errors)
                self.assertIn('word_info', inspect(create_engine('sqlite:///' + path)).get_table_names())
