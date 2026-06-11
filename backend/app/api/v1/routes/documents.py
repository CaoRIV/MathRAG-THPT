from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_container
from app.container import ServiceContainer
from app.schemas.api import DocumentDetail, DocumentSection, RelatedDocument

router = APIRouter()


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: str,
    container: ServiceContainer = Depends(get_container),
) -> DocumentDetail:
    chunks = [item for item in container.documents if item.document_id == document_id]
    if not chunks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    first = chunks[0]
    formulas = list(dict.fromkeys(formula for chunk in chunks for formula in chunk.formulas))
    related = []
    for item in container.documents:
        if item.document_id == document_id or item.topic != first.topic:
            continue
        if item.document_id not in {doc.id for doc in related}:
            related.append(
                RelatedDocument(
                    id=item.document_id,
                    title=item.title,
                    topic=item.topic,
                    content_type=item.content_type,
                    source_url=item.source_url,
                )
            )
    return DocumentDetail(
        id=first.document_id,
        title=first.title,
        description=f"Tài liệu {first.content_type} thuộc chủ đề {first.topic}.",
        grade=first.grade,
        topic=first.topic,
        content_type=first.content_type,
        source_url=first.source_url,
        sections=[
            DocumentSection(
                id=item.chunk_id,
                heading=item.title,
                content=item.content,
                content_type=item.content_type,
                page_number=item.page_number,
                formulas=item.formulas,
            )
            for item in chunks
        ],
        formulas=formulas,
        related_documents=related[:4],
    )

