from src.interfaces.content_provider import IContentProvider
from src.interfaces.social_client import ISocialClient

class PostService:
    def __init__(self, content_provider: IContentProvider, social_client: ISocialClient):
        self.content_provider = content_provider
        self.social_client = social_client

    def create_and_publish_post(self) -> bool:
        """Assembles the post text, link, and image using the provider, then publishes it."""
        print("Starting post creation process...")
        
        # 1. Load contents via provider
        text, image_path = self.content_provider.get_post_content()
        
        print(f"Prepared Text:\n{text}")
        print(f"Selected Image: {image_path}")

        # 2. Publish via social client
        success = self.social_client.publish_post(text, image_path)
        
        if success:
            self.content_provider.mark_as_published()
            print("Content marked as successfully published.")
        else:
            print("Post failed. Content was not deleted from the queue.")
            
        return success
