import json
from typing import Generator


class innertube_parser:
    def __init__(self):
        self.continuation_token = None

    def _response_type(self, response: dict) -> str | None:
        """
        Determine the type of response based on its structure.
        returns:
            "initial": If the response contains the initial page structure.
            "continuation": If the response contains continuation items.
            None: If the response type cannot be determined.
        """
        content = response.get("contents",{})
        if any(
            key in response for key in ["onResponseReceivedActions", 
                                       "onResponseReceivedEndpoints",
                                       "continuationContents"]
        ):
            return "continuation"
        if isinstance(content, dict) and "twoColumnBrowseResultsRenderer" in content:
            return "initial"
        
        return None
        
            

    def _text(self, data: dict) -> str | None:
        """Read text from either YouTube text format."""
        if not data:return None

        text = data.get("simpleText") or data.get("content")
        if text:return text

        text_parts = []
        for run in data.get("runs", []):
            text_parts.append(run.get("text", ""))

        full_text = "".join(text_parts)
        return full_text or None

    def _thumb(self, thumbnails: list) -> str | None:
        """Use the last thumbnail because YouTube normally orders them by size."""
        if not thumbnails:
            return None
        return thumbnails[-1].get("url")

    def _parse_lockup(self, lockup: dict) -> dict | None:
        """Parse a newer lockupViewModel video or playlist card."""
        media_id = lockup.get("contentId")
        media_type = lockup.get("contentType")

        if media_type == "LOCKUP_CONTENT_TYPE_VIDEO":
            url = f"https://www.youtube.com/watch?v={media_id}"
        elif media_type == "LOCKUP_CONTENT_TYPE_PLAYLIST":
            url = f"https://www.youtube.com/playlist?list={media_id}"
        else:
            return None

        metadata = lockup.get("metadata", {}).get("lockupMetadataViewModel", {})
        title = self._text(metadata.get("title", {}))

        image = lockup.get("contentImage", {})
        thumbnail = image.get("thumbnailViewModel", {})
        if not thumbnail:
            thumbnail = (
                image.get("collectionThumbnailViewModel", {})
                .get("primaryThumbnail", {})
                .get("thumbnailViewModel", {})
            )
        thumbnails = thumbnail.get("image", {}).get("sources", [])

        rows = (
            metadata.get("metadata", {})
            .get("contentMetadataViewModel", {})
            .get("metadataRows", [])
        )
        channel = None
        if rows and rows[0].get("metadataParts"):
            channel = self._text(rows[0]["metadataParts"][0].get("text", {}))

        if not media_id or not title:
            return None

        return {
            "url": url,
            "title": title,
            "channel": channel,
            "thumb": self._thumb(thumbnails),
        }

    def _parse_grid_playlist(self, playlist: dict) -> dict | None:
        """Parse an older gridPlaylistRenderer playlist card."""
        playlist_id = playlist.get("playlistId")
        title = self._text(playlist.get("title", {}))

        thumbnails = playlist.get("thumbnail", {}).get("thumbnails", [])
        if not thumbnails:
            thumbnails = (
                playlist.get("thumbnailRenderer", {})
                .get("playlistVideoThumbnailRenderer", {})
                .get("thumbnail", {})
                .get("thumbnails", [])
            )

        channel_data = playlist.get("shortBylineText", {}) or playlist.get("ownerText", {})
        channel = self._text(channel_data)

        if not playlist_id or not title:
            return None

        return {
            "url": f"https://www.youtube.com/playlist?list={playlist_id}",
            "title": title,
            "channel": channel,
            "thumb": self._thumb(thumbnails),
        }

    def _parse_playlist_video(self, video: dict) -> dict | None:
        """Parse an older playlistVideoRenderer video card."""
        video_id = video.get("videoId")
        title = self._text(video.get("title", {}))
        channel = self._text(video.get("shortBylineText", {}))
        thumbnails = video.get("thumbnail", {}).get("thumbnails", [])

        if not video_id or not title:
            return None

        return {
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": title,
            "channel": channel,
            "thumb": self._thumb(thumbnails),
        }

    def _parse_video(self, video: dict) -> dict | None:
        """Parse an older videoRenderer video card."""
        video_id = video.get("videoId")
        title = self._text(video.get("title", {}))
        channel_data = video.get("ownerText", {}) or video.get("shortBylineText", {})
        channel = self._text(channel_data)
        thumbnails = video.get("thumbnail", {}).get("thumbnails", [])

        if not video_id or not title:
            return None

        return {
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": title,
            "channel": channel,
            "thumb": self._thumb(thumbnails),
        }
    

    def _parse_continuation(self, continuation: dict) -> None:
        """Parse supported continuation item token structures."""
        token = None

        view_model = continuation.get("continuationItemViewModel", {})
        if view_model:
            token = (
                view_model.get("continuationCommand", {})
                .get("innertubeCommand", {})
                .get("continuationCommand", {})
                .get("token")
            )

        renderer = continuation.get("continuationItemRenderer", {})
        if renderer and not token:
            endpoint = renderer.get("continuationEndpoint", {})
            token = endpoint.get("continuationCommand", {}).get("token")

            if not token:
                commands = (
                    endpoint.get("commandExecutorCommand", {})
                    .get("commands", [])
                )
                for command in commands:
                    token = command.get("continuationCommand", {}).get("token")
                    if token:
                        break

        if token:
            self.continuation_token = token

        
    def _walk_to_entry(self, node: dict) -> list:
        """Get the first list of page entries under tabRenderer.content."""
        playlist = self._account_info_walk(node, "playlistVideoListRenderer")
        if playlist:
            return playlist.get("contents", [])

        for renderer_name in ("richGridRenderer", "sectionListRenderer"):
            if renderer_name in node:
                return node[renderer_name].get("contents", [])

        if "gridRenderer" in node:
            return node["gridRenderer"].get("items", [])

        return []

    def _walk(self, node) -> Generator[dict, None, None]:
        """Walk through wrappers until a media card is found."""
        if isinstance(node, dict):
            if "lockupViewModel" in node:
                media = self._parse_lockup(node["lockupViewModel"])
                if media:
                    yield media
                return

            if "playlistVideoRenderer" in node:
                media = self._parse_playlist_video(node["playlistVideoRenderer"])
                if media:
                    yield media
                return

            if "videoRenderer" in node:
                media = self._parse_video(node["videoRenderer"])
                if media:
                    yield media
                return

            if "gridPlaylistRenderer" in node:
                media = self._parse_grid_playlist(node["gridPlaylistRenderer"])
                if media:
                    yield media
                return
            
            if "continuationItemViewModel" in node or "continuationItemRenderer" in node and self.continuation_token is None:
                self._parse_continuation(node)
                return

            for value in node.values():
                yield from self._walk(value)

        elif isinstance(node, list):
            for value in node:
                yield from self._walk(value)


    def _continuation_walk_to_entry(self, continuation_response: dict) -> list:
        
        entries = []
        
        for action in continuation_response.get("onResponseReceivedActions", []):
            append_action = action.get("appendContinuationItemsAction")
            if append_action:
                entries = append_action.get("continuationItems", [])
                break
        
        return entries

    def _selected_home_grid(self, data: dict) -> dict:
        """
        Get content from the selected YouTube tab.
        > will raise keyerr for continnation 

        """
        tabs = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]

        selected_tab = next(
            tab["tabRenderer"]
            for tab in tabs
            if tab.get("tabRenderer", {}).get("selected")
        )
        return selected_tab["content"]
    
    def get_continuation_token(self) -> str | None:
        """
        Get the continuation token belonging to the main grid.\n
        ### IMPORTANT: This method should be called after parse() to ensure the continuation token is updated.
        """
        return self.continuation_token

    def _account_info_walk(
        self,
        node: dict|list,
        renderer: str = "activeAccountHeaderRenderer",
    ) -> dict | None:
        if isinstance(node, dict):
            header = node.get(renderer)
            if isinstance(header, dict):
                return header
            
            for value in node.values():
                if result:= self._account_info_walk(value, renderer):
                    return result
        
        elif isinstance(node, list):
            for value in node:
                if result:= self._account_info_walk(value, renderer):
                    return result
        return None
                                        
    def parse_account_info(self, json_data: dict) -> dict | None:
        header = self._account_info_walk(json_data)
        if not header:
            return None

        thumbnail = header.get("accountPhoto", {}).get("thumbnails", [])
        return {
            "name": self._text(header.get("accountName", {})),
            "thumb": self._thumb(thumbnail),
        }

    
    def parse(self, 
              json_data: dict,
              contiunation_page:bool = False) -> list:
        """Return every media card in the selected tab."""

        self.continuation_token = None
        response_type = "continuation" if contiunation_page else "initial"
        print(f"Response type: {response_type}")
        entries = []
        try:
            if response_type == "continuation":
                entries = self._continuation_walk_to_entry(json_data)
                
            elif response_type == "initial":
                content = self._selected_home_grid(json_data)
                entries = self._walk_to_entry(content)
            if entries:
                return list(self._walk(entries))
            else:
                return []
        except KeyError:
            return []


