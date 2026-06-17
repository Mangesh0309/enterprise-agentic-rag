from app.retrieval.bm25 import bm25_rank
from app.retrieval.hybrid import RetrievedChunk, weighted_merge


def chunk(chunk_id: str, text: str, score: float) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc",
        document_title="Policy",
        workspace_id="hr",
        text=text,
        score=score,
    )


def test_weighted_merge_combines_dense_and_keyword_scores():
    dense = [chunk("a", "leave policy", 0.9), chunk("b", "payroll", 0.3)]
    keyword = [chunk("b", "payroll policy", 0.8), chunk("c", "benefits", 0.5)]

    result = weighted_merge(dense, keyword, dense_weight=0.6, keyword_weight=0.4, top_k=2)

    assert [item.chunk_id for item in result] == ["a", "b"]
    assert result[0].score >= result[1].score


def test_bm25_rank_prioritizes_keyword_overlap():
    chunks = [
        chunk("a", "engineering handbook deployment incident review", 0),
        chunk("b", "finance reimbursement invoice payment", 0),
    ]

    result = bm25_rank("deployment review", chunks, top_k=1)

    assert result[0].chunk_id == "a"
