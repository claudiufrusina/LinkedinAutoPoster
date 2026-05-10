from typing import Protocol, Optional, Tuple

class IContentProvider(Protocol):
    def get_post_content(self) -> Tuple[str, Optional[str]]:
        """
        Retrieves the finalized content for the next post.
        
        Returns:
            Tuple[str, Optional[str]]: 
                - The complete text/caption for the post.
                - The absolute path to an image file, or None if it's a text-only post.
        """
        ...

    def mark_as_published(self) -> None:
        """
        Confirms that the retrieved content was successfully published.
        This allows the provider to safely delete or mark the content as used.
        """
        ...
