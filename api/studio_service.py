"""
Studio service layer for flashcard and mindmap generation.
"""

import json
from typing import Any, Dict, List, Optional

from loguru import logger

from open_notebook.domain.notebook import Note, Notebook
from open_notebook.graphs.studio import flashcard_graph, mindmap_graph


class StudioService:
    """Service layer for studio operations (flashcards, mindmap)."""

    def __init__(self):
        logger.info("Studio service initialized")

    async def get_flashcards(self, notebook_id: str) -> List[Dict[str, Any]]:
        """Get all flashcards for a notebook."""
        notebook = await Notebook.get(notebook_id)
        if not notebook:
            return []

        notes = await notebook.get_notes()
        flashcards = []
        for note in notes:
            if note.note_type == "flashcard" and note.content:
                try:
                    card_data = json.loads(note.content)
                    if isinstance(card_data, dict) and "question" in card_data:
                        flashcards.append({
                            "id": note.id,
                            "question": card_data.get("question", ""),
                            "answer": card_data.get("answer", ""),
                            "source_ids": card_data.get("source_ids", []),
                            "created": note.created,
                        })
                except json.JSONDecodeError:
                    continue
        return flashcards

    async def generate_flashcards(
        self,
        notebook_id: str,
        source_ids: Optional[List[str]] = None,
        count: int = 10,
    ) -> List[Dict[str, Any]]:
        """Generate flashcards from notebook sources."""
        notebook = await Notebook.get(notebook_id)
        if not notebook:
            raise ValueError(f"Notebook {notebook_id} not found")

        sources = await notebook.get_sources()
        if not sources:
            raise ValueError("No sources found in notebook")

        # Filter by source_ids if provided
        if source_ids:
            sources = [s for s in sources if s.id in source_ids]

        if not sources:
            raise ValueError("No matching sources found")

        # Re-fetch sources with full_text included (get_sources omits it for performance)
        from open_notebook.domain.notebook import Source
        sources_with_text = []
        for s in sources:
            full_source = await Source.get(s.id)
            if full_source and full_source.full_text:
                sources_with_text.append(full_source)

        if not sources_with_text:
            raise ValueError("No text content available from sources")

        # Combine source texts
        combined_text = "\n\n".join([
            f"Source: {s.title or 'Untitled'}\n{s.full_text or ''}"
            for s in sources_with_text
        ])

        logger.info(f"Studio generation: found {len(sources_with_text)} sources with text, combined_text length: {len(combined_text)}")

        # Generate flashcards via LangGraph
        # Pass template name and input_text to graph for proper rendering
        logger.info("Invoking flashcard_graph.ainvoke()...")
        try:
            result = await flashcard_graph.ainvoke({
                "template_name": "studio/flashcard",
                "input_text": combined_text,
            })
            logger.info(f"Flashcard graph completed, result keys: {result.keys()}")
        except Exception as e:
            logger.error(f"Flashcard graph invocation failed: {str(e)}")
            raise

        output = result.get("output", "")
        if not output:
            raise ValueError("Failed to generate flashcards")

        logger.info(f"Flashcard raw output: {output[:500]}...")

        # Parse JSON output
        try:
            cards = json.loads(output)
            if not isinstance(cards, list):
                cards = [cards]
            logger.info(f"Successfully parsed {len(cards)} flashcards")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}, output was: {output}")
            raise ValueError("Failed to parse generated flashcards")

        # Create Note records for flashcards
        created_cards = []
        source_ids_list = [s.id for s in sources_with_text]

        for card in cards[:count]:
            if isinstance(card, dict) and "question" in card:
                card_content = json.dumps({
                    "question": card["question"],
                    "answer": card["answer"],
                    "source_ids": source_ids_list,
                })
                note = Note(
                    title=f"Flashcard: {card['question'][:50]}...",
                    content=card_content,
                    note_type="flashcard",
                )
                await note.save()
                await note.add_to_notebook(notebook_id)

                created_cards.append({
                    "id": note.id,
                    "question": card["question"],
                    "answer": card["answer"],
                    "source_ids": source_ids_list,
                    "created": note.created,
                })

        return created_cards

    async def delete_flashcards(self, notebook_id: str) -> bool:
        """Delete all flashcards for a notebook."""
        notebook = await Notebook.get(notebook_id)
        if not notebook:
            return False

        notes = await notebook.get_notes()
        for note in notes:
            if note.note_type == "flashcard":
                await note.delete()
        return True

    async def get_mindmap(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """Get mindmap for a notebook."""
        notebook = await Notebook.get(notebook_id)
        if not notebook:
            return None

        notes = await notebook.get_notes()
        for note in notes:
            if note.note_type == "mindmap" and note.content:
                return {
                    "id": note.id,
                    "content": note.content,
                    "created": note.created,
                }
        return None

    async def generate_mindmap(
        self,
        notebook_id: str,
        source_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate mindmap from notebook sources."""
        notebook = await Notebook.get(notebook_id)
        if not notebook:
            raise ValueError(f"Notebook {notebook_id} not found")

        sources = await notebook.get_sources()
        if not sources:
            raise ValueError("No sources found in notebook")

        # Filter by source_ids if provided
        if source_ids:
            sources = [s for s in sources if s.id in source_ids]

        if not sources:
            raise ValueError("No matching sources found")

        # Re-fetch sources with full_text included (get_sources omits it for performance)
        from open_notebook.domain.notebook import Source
        sources_with_text = []
        for s in sources:
            full_source = await Source.get(s.id)
            if full_source and full_source.full_text:
                sources_with_text.append(full_source)

        if not sources_with_text:
            raise ValueError("No text content available from sources")

        # Combine source texts
        combined_text = "\n\n".join([
            f"Source: {s.title or 'Untitled'}\n{s.full_text or ''}"
            for s in sources_with_text
        ])

        logger.info(f"Studio generation: found {len(sources_with_text)} sources with text, combined_text length: {len(combined_text)}")

        # Generate mindmap via LangGraph
        # Pass template name and input_text to graph for proper rendering
        logger.info("Invoking mindmap_graph.ainvoke()...")
        try:
            result = await mindmap_graph.ainvoke({
                "template_name": "studio/mindmap",
                "input_text": combined_text,
            })
            logger.info(f"Mindmap graph completed, result keys: {result.keys()}")
        except Exception as e:
            logger.error(f"Mindmap graph invocation failed: {str(e)}")
            raise

        output = result.get("output", "")
        if not output:
            raise ValueError("Failed to generate mindmap")

        # Clean up the output (ensure it starts with "mindmap")
        output = output.strip()
        if not output.startswith("mindmap"):
            output = "mindmap\n" + output

        # Delete existing mindmap if any
        await self.delete_mindmap(notebook_id)

        # Create Note record for mindmap
        note = Note(
            title="Mind Map",
            content=output,
            note_type="mindmap",
        )
        await note.save()
        await note.add_to_notebook(notebook_id)

        return {
            "id": note.id,
            "content": output,
            "created": note.created,
        }

    async def delete_mindmap(self, notebook_id: str) -> bool:
        """Delete mindmap for a notebook."""
        notebook = await Notebook.get(notebook_id)
        if not notebook:
            return False

        notes = await notebook.get_notes()
        for note in notes:
            if note.note_type == "mindmap":
                await note.delete()
        return True


# Global service instance
studio_service = StudioService()