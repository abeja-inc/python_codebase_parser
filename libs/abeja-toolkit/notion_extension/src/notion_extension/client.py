from typing import Any

from notion_client import AsyncClient as _AsyncClient
from notion_client import Client as _Client
from notion_client.helpers import async_collect_paginated_api, collect_paginated_api
from notion_client.typing import SyncAsync

from .blocks import Blocks
from .db_properties import Properties


class Client(_Client):
    """
    A wrapper class for the Notion API synchronous client.
    This class provides additional methods to interact with the Notion API.

    Args:
        auth: Bearer token for authentication. If left undefined, the `auth` parameter
            should be set on each request.
        timeout_ms: Number of milliseconds to wait before emitting a
            `RequestTimeoutError`.
        base_url: The root URL for sending API requests. This can be changed to test with
            a mock server.
        log_level: Verbosity of logs the instance will produce. By default, logs are
            written to `stdout`.
        logger: A custom logger.
        notion_version: Notion version to use.


    Attributes:
        pages (notion_client.Client.pages): The pages API client.
            See: https://developers.notion.com/reference/page
        databases (notion_client.Client.databases): The databases API client.
            See: https://developers.notion.com/reference/database
        blocks (notion_client.Client.blocks): The blocks API client.
            See: https://developers.notion.com/reference/block
        users (notion_client.Client.users): The users API client.
            See: https://developers.notion.com/reference/user
        search (notion_client.Client.search): The search API client.
            See: https://developers.notion.com/reference/post-search
        comments (notion_client.Client.comments): The comments API client.
            See: https://developers.notion.com/reference/create-a-comment
    """

    def create_page(
        self,
        database_id: str,
        properties: Properties,
        page_contents: Blocks | None = None,
    ) -> SyncAsync[Any]:
        """
        Create a new page in the Notion database.

        Parameters
        ----------
        database_id: str
            The ID of the database where the page will be created.
        properties: Properties
            The properties of the page.
        page_contents: Blocks | None, optional
            The contents of the page. Defaults to None.

        Returns
        ----------
        SyncAsync[Any]
            The response of the API request.
        """
        if page_contents:
            return self.pages.create(
                parent={"database_id": database_id},
                properties=properties.format(),
                children=page_contents.format(),
            )

        return self.pages.create(
            parent={"database_id": database_id},
            properties=properties.format(),
        )

    def get_all_users(self) -> list[dict[str, Any]]:
        """
        Get all users in the workspace. This method fetch all pagenated users.

        Returns
        -------
        list[dict[str, Any]]
            The list of users in the workspace.
        """
        return collect_paginated_api(self.users.list)

    def get_user_info(self, email: str) -> dict[str, Any]:
        """
        Get the information of a user by email.

        Parameters
        ----------
        email: str
            The email of the user.

        Returns
        -------
        dict[str, Any]
            The information of the user.
        """
        users = self.get_all_users()
        return [user for user in users if user.get("person", {}).get("email") == email][0]

    def get_entire_database(
        self, database_id: str, filter: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Get the entire database content. This method fetch all pagenated database content.

        Parameters
        ----------
        database_id: str
            The ID of the database you want to fetch.
        filter: dict[str, Any] | None, optional
            The filter to apply. Defaults to None.
            See: https://developers.notion.com/reference/post-database-query-filter

        Returns
        -------
        list[dict[str, Any]]
            The entire database content.
        """
        kwargs: dict[str, Any] = {"database_id": database_id}
        if filter:
            kwargs["filter"] = filter
        return collect_paginated_api(self.databases.query, **kwargs)

    def get_all_blocks(self, page_id: str) -> list[dict[str, Any]]:
        """
        Get all blocks of a page. This method fetch all pagenated blocks.

        Parameters
        ----------
        page_id: str
            The ID of the page you want to get the contents.

        Returns
        -------
        list[dict[str, Any]]
            The list of blocks of the page.
        """
        blocks: list[dict[str, Any]] = collect_paginated_api(
            self.blocks.retrieve, block_id=f"{page_id}/children"
        )

        output = []
        for block in blocks:
            if block.get("has_children"):
                block["children"] = self.get_all_blocks(block["id"])

            output.append(block)

        return output

    def append_blocks_to_page(self, page_id: str, blocks: Blocks) -> SyncAsync[Any]:
        """
        Append blocks to a page.

        Parameters
        ----------
        page_id: str
            The ID of the page you want to append the blocks.
        blocks: Blocks
            The blocks to append.

        Returns
        -------
        SyncAsync[Any]
            The response of the API request.
        """
        return self.blocks.children.append(
            block_id=page_id,
            children=blocks.format(),
        )


class AsyncClient(_AsyncClient):
    """
    A wrapper class for the Notion API asynchronous client.
    This class provides additional methods to interact with the Notion API.

    Args:
        auth: Bearer token for authentication. If left undefined, the `auth` parameter
            should be set on each request.
        timeout_ms: Number of milliseconds to wait before emitting a
            `RequestTimeoutError`.
        base_url: The root URL for sending API requests. This can be changed to test with
            a mock server.
        log_level: Verbosity of logs the instance will produce. By default, logs are
            written to `stdout`.
        logger: A custom logger.
        notion_version: Notion version to use.


    Attributes:
        pages (notion_client.Client.pages): The pages API client.
            See: https://developers.notion.com/reference/page
        databases (notion_client.Client.databases): The databases API client.
            See: https://developers.notion.com/reference/database
        blocks (notion_client.Client.blocks): The blocks API client.
            See: https://developers.notion.com/reference/block
        users (notion_client.Client.users): The users API client.
            See: https://developers.notion.com/reference/user
        search (notion_client.Client.search): The search API client.
            See: https://developers.notion.com/reference/post-search
        comments (notion_client.Client.comments): The comments API client.
            See: https://developers.notion.com/reference/create-a-comment
    """

    async def create_page(
        self,
        database_id: str,
        properties: Properties,
        page_contents: Blocks | None = None,
    ) -> SyncAsync[Any]:
        """
        Create a new page in the Notion database.

        Parameters
        ----------
        database_id: str
            The ID of the database where the page will be created.
        properties: Properties
            The properties of the page.
        page_contents: Blocks | None, optional
            The contents of the page. Defaults to None.

        Returns
        ----------
        dict[str, dict[str, str]]
            The created page.
        """
        if page_contents:
            return await self.pages.create(
                parent={"database_id": database_id},
                properties=properties.format(),
                children=page_contents.format(),
            )

        return await self.pages.create(
            parent={"database_id": database_id},
            properties=properties.format(),
        )

    async def get_all_users(self) -> list[dict[str, Any]]:
        """
        Get all users in the workspace. This method fetch all pagenated users.

        Returns
        -------
        list[dict[str, Any]]
            The list of users in the workspace.
        """
        return await async_collect_paginated_api(self.users.list)

    async def get_user_info(self, email: str) -> dict[str, Any]:
        """
        Get the information of a user by email.

        Parameters
        ----------
        email: str
            The email of the user.

        Returns
        -------
        dict[str, Any]
            The information of the user.
        """
        users = await self.get_all_users()
        return [user for user in users if user.get("person", {}).get("email") == email][0]

    async def get_entire_database(
        self, database_id: str, filter: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Get the entire database content. This method fetch all pagenated database content.

        Parameters
        ----------
        database_id: str
            The ID of the database you want to fetch.
        filter: dict[str, Any] | None, optional
            The filter to apply. Defaults to None.
            See: https://developers.notion.com/reference/post-database-query-filter

        Returns
        -------
        list[dict[str, Any]]
            The entire database content.
        """
        kwargs: dict[str, Any] = {"database_id": database_id}
        if filter:
            kwargs["filter"] = filter
        return await async_collect_paginated_api(self.databases.query, **kwargs)

    async def get_all_blocks(self, page_id: str) -> list[dict[str, Any]]:
        """
        Get all blocks of a page. This method fetch all pagenated blocks.

        Parameters
        ----------
        page_id: str
            The ID of the page you want to get the contents.

        Returns
        -------
        list[dict[str, Any]]
            The list of blocks of the page.
        """
        blocks: list[dict[str, Any]] = await async_collect_paginated_api(
            self.blocks.retrieve, block_id=f"{page_id}/children"
        )

        output = []
        for block in blocks:
            if block.get("has_children"):
                block["children"] = await self.get_all_blocks(block["id"])

            output.append(block)

        return output

    async def append_blocks_to_page(self, page_id: str, blocks: Blocks) -> SyncAsync[Any]:
        """
        Append blocks to a page.

        Parameters
        ----------
        page_id: str
            The ID of the page you want to append the blocks.
        blocks: Blocks
            The blocks to append.

        Returns
        -------
        SyncAsync[Any]
            The response of the API request.
        """
        return await self.blocks.children.append(
            block_id=page_id,
            children=blocks.format(),
        )
