import pytest
from hypothesis import given, settings, strategies as st

from btreedict import BTreeDict

sortedcontainers = pytest.importorskip("sortedcontainers")
SortedDict = sortedcontainers.SortedDict


@settings(max_examples=200, deadline=None)
@given(
    st.lists(
        st.tuples(
            st.sampled_from(["insert", "delete", "get", "contains"]),
            st.integers(min_value=0, max_value=100),
            st.integers(min_value=-1000, max_value=1000),
        ),
        min_size=1,
        max_size=200,
    )
)
def test_random_ops_match_sorteddict(ops):
    bt = BTreeDict()
    sd = SortedDict()

    for op, key, value in ops:
        if op == "insert":
            bt[key] = value
            sd[key] = value
        elif op == "delete":
            if key in sd:
                del bt[key]
                del sd[key]
            else:
                with pytest.raises(KeyError):
                    del bt[key]
        elif op == "get":
            assert bt.get(key) == sd.get(key)
        elif op == "contains":
            assert (key in bt) == (key in sd)

        assert len(bt) == len(sd)
        assert bt.keys() == list(sd.keys())
        assert bt.values() == list(sd.values())
        assert bt.items() == list(sd.items())


@settings(max_examples=200, deadline=None)
@given(
    st.lists(st.integers(min_value=-50, max_value=50), min_size=0, max_size=200),
    st.one_of(st.none(), st.integers(min_value=-60, max_value=60)),
    st.one_of(st.none(), st.integers(min_value=-60, max_value=60)),
    st.tuples(st.booleans(), st.booleans()),
)
def test_irange_matches_sorteddict(keys, min_v, max_v, inclusive):
    bt = BTreeDict()
    sd = SortedDict()
    for k in keys:
        bt[k] = k
        sd[k] = k

    bt_result = list(bt.irange(min_v, max_v, inclusive=inclusive))
    sd_result = list(sd.irange(min_v, max_v, inclusive=inclusive))
    assert bt_result == sd_result
