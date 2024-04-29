"""
    Pydantic models definition used within the news data pipeline.
    Implementation contains models for different NewsArticle formats:
    - NewsDataIOModel: Model for NewsDataIO API response.
    - NewsAPIModel: Model for NewsAPI response.
    
    Rest of the models are used for data processing and exchange within the pipeline:
    - CommonDocument: Common representation of a news article.
    - RefinedDocument: Refined version of a CommonDocument.
    - ChunkedDocument: Chunked version of a RefinedDocument.
    - EmbeddedDocument: Embedded version of a ChunkedDocument.
     
"""

import datetime
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from dateutil import parser
# from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field, field_validator
# from unstructured.staging.huggingface import chunk_by_attention_window

from cleaners import clean_full, normalize_whitespace, remove_html_tags
# from embeddings import TextEmbedder

logger = logging.getLogger(__name__)

class DocumentSource(BaseModel):
    id: Optional[str]
    name: str


class CommonDocument(BaseModel):
    article_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(default_factory=lambda: "N/A")
    url: str = Field(default_factory=lambda: "N/A")
    published_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    source_name: str = Field(default_factory=lambda: "Unknown")
    image_url: Optional[str] = Field(default_factory=lambda: None)
    author: Optional[str] = Field(default_factory=lambda: "Unknown")
    description: Optional[str] = Field(default_factory=lambda: None)
    content: Optional[str] = Field(default_factory=lambda: None)

    @field_validator("title", "description", "content")
    def clean_text_fields(cls, v):
        if v is None or v == "":
            return "N/A"
        return clean_full(v)

    @field_validator("url", "image_url")
    def clean_url_fields(cls, v):
        if v is None:
            return "N/A"
        v = remove_html_tags(v)
        v = normalize_whitespace(v)
        return v

    @field_validator("published_at")
    def clean_date_field(cls, v):
        try:
            parsed_date = parser.parse(v)
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            logger.error(f"Error parsing date: {v}, using current date instead.")

    @classmethod
    def from_json(cls, data: dict) -> "CommonDocument":
        """Create a CommonDocument from a JSON object."""
        return cls(**data)

    def to_kafka_payload(self) -> dict:
        """Prepare the common representation for Kafka payload."""
        return self.model_dump(exclude_none=False)


class NewsDataIOModel(BaseModel):
    article_id: str
    title: str
    link: str
    description: Optional[str]
    pubDate: str
    source_id: Optional[str]
    source_url: Optional[str]
    source_icon: Optional[str]
    creator: Optional[List[str]]
    image_url: Optional[str]
    content: Optional[str]

    def to_common(self) -> CommonDocument:
        """Convert to common news article format."""
        return CommonDocument(
            article_id=self.article_id,
            title=self.title,
            description=self.description,
            url=self.link,
            published_at=self.pubDate,
            source_name=self.source_id or "Unknown",
            image_url=self.image_url,
            author=", ".join(self.creator) if self.creator else None,
            content=self.content,
        )


class NewsAPIModel(BaseModel):
    source: DocumentSource
    author: Optional[str]
    title: str
    description: Optional[str]
    url: str
    urlToImage: Optional[str]
    publishedAt: str
    content: Optional[str]

    def to_common(self) -> CommonDocument:
        """Convert to common news article format."""
        return CommonDocument(
            title=self.title,
            description=self.description,
            url=self.url,
            published_at=self.publishedAt,
            source_name=self.source.name,
            source_id=self.source.id,
            author=self.author,
            image_url=self.urlToImage,
            content=self.content,
        )