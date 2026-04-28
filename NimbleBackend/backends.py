# NimbleBackend/backends.py
from django.core.files.storage import Storage
from django.conf import settings
from vercel_blob import put
import os

class VercelBlobStorage(Storage):
    def _save(self, name, content):
        # Cleans the path for Vercel's flat structure
        filename = os.path.basename(name)
        
        # Uploads the file to Vercel Blob
        # Note: BLOB_READ_WRITE_TOKEN must be in your Env Vars
        resp = put(filename, content.read(), {"access": "public"})
        
        # We return the handle/url provided by Vercel
        return resp['url']

    def url(self, name):
        # 'name' here is the URL returned by the _save method
        return name

    def exists(self, name):
        # Serverless storage usually handles overwrites/naming internally
        return False