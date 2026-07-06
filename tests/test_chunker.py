from ragops.ingestion.chunkers import header_aware_chunks


def test_header_aware_chunks_returns_content():
    text = "# Title\n" + "This is a sentence. " * 120
    chunks = header_aware_chunks(text, max_chars=300, overlap=50)
    assert len(chunks) > 1
    assert all(chunk.text for chunk in chunks)
    assert chunks[0].section_title == "Title"
