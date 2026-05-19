from typing import Protocol, Optional, List


class IPostRepository(Protocol):
    """
    Defines CRUD operations for managing LinkedIn posts.
    
    This interface is separate from IContentProvider (which is read-only and 
    publishing-oriented) following the Interface Segregation Principle (ISP).
    """

    def list_posts(self, status_filter: str = "all") -> List[dict]:
        """
        Retrieves all posts with optional status filtering.
        
        Args:
            status_filter: One of 'all', 'pending', 'published'.
            
        Returns:
            List of dicts with merged link + text data for each post.
        """
        ...

    def get_post(self, post_id: str) -> Optional[dict]:
        """
        Retrieves a single post by its ID.
        
        Args:
            post_id: The unique post identifier.
            
        Returns:
            A dict with merged link + text data, or None if not found.
        """
        ...

    def create_post(self, data: dict) -> bool:
        """
        Creates a new post by inserting into both links and texts tables.
        
        Args:
            data: Dict containing all post fields (id, title, url, body, 
                  hashtags, image, expiration_date, company_name, company_urn).
                  
        Returns:
            True if the post was created successfully, False otherwise.
        """
        ...

    def update_post(self, post_id: str, data: dict) -> bool:
        """
        Updates an existing post.
        
        Args:
            post_id: The unique post identifier.
            data: Dict containing the fields to update.
            
        Returns:
            True if the post was updated successfully, False otherwise.
        """
        ...

    def delete_post(self, post_id: str) -> bool:
        """
        Deletes a post from both links and texts tables.
        
        Args:
            post_id: The unique post identifier.
            
        Returns:
            True if the post was deleted successfully, False otherwise.
        """
        ...

    def reset_post(self, post_id: str) -> bool:
        """
        Resets a published post back to pending status.
        Sets links.published = 0 and texts.last_published = NULL.
        
        Args:
            post_id: The unique post identifier.
            
        Returns:
            True if the post was reset successfully, False otherwise.
        """
        ...
