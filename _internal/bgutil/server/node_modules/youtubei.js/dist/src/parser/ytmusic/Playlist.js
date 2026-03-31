// noinspection ES6MissingAwait
import { MusicPlaylistShelfContinuation, Parser, SectionListContinuation } from '../index.js';
import MusicCarouselShelf from '../classes/MusicCarouselShelf.js';
import MusicDetailHeader from '../classes/MusicDetailHeader.js';
import MusicEditablePlaylistDetailHeader from '../classes/MusicEditablePlaylistDetailHeader.js';
import MusicPlaylistShelf from '../classes/MusicPlaylistShelf.js';
import MusicShelf from '../classes/MusicShelf.js';
import SectionList from '../classes/SectionList.js';
import MusicResponsiveListItem from '../classes/MusicResponsiveListItem.js';
import MusicResponsiveHeader from '../classes/MusicResponsiveHeader.js';
import { InnertubeError } from '../../utils/Utils.js';
import { observe } from '../helpers.js';
import ContinuationItem from '../classes/ContinuationItem.js';
import AppendContinuationItemsAction from '../classes/actions/AppendContinuationItemsAction.js';
export default class Playlist {
    #page;
    #actions;
    #continuation;
    header;
    contents;
    background;
    #last_fetched_suggestions;
    #suggestions_continuation;
    constructor(response, actions) {
        this.#actions = actions;
        this.#page = Parser.parseResponse(response.data);
        this.#last_fetched_suggestions = null;
        this.#suggestions_continuation = null;
        if (this.#page.continuation_contents) {
            const data = this.#page.continuation_contents?.as(MusicPlaylistShelfContinuation);
            if (!data.contents)
                throw new InnertubeError('No contents found in the response');
            this.contents = data.contents.as(MusicResponsiveListItem, ContinuationItem);
            const continuation_item = this.contents.firstOfType(ContinuationItem);
            this.#continuation = data.continuation || continuation_item;
        }
        else if (this.#page.contents_memo) {
            this.header = this.#page.contents_memo.getType(MusicResponsiveHeader, MusicEditablePlaylistDetailHeader, MusicDetailHeader)?.[0];
            this.contents = this.#page.contents_memo.getType(MusicPlaylistShelf)?.[0]?.contents.as(MusicResponsiveListItem, ContinuationItem) || observe([]);
            this.background = this.#page.background;
            const continuation_item = this.contents.firstOfType(ContinuationItem);
            this.#continuation = this.#page.contents_memo.getType(MusicPlaylistShelf)?.[0]?.continuation || continuation_item;
        }
        else if (this.#page.on_response_received_actions) {
            const append_continuation_action = this.#page.on_response_received_actions.firstOfType(AppendContinuationItemsAction);
            this.contents = append_continuation_action?.contents?.as(MusicResponsiveListItem, ContinuationItem);
            this.#continuation = this.contents?.firstOfType(ContinuationItem);
        }
    }
    /**
     * Retrieves playlist items continuation.
     */
    async getContinuation() {
        if (!this.#continuation)
            throw new InnertubeError('Continuation not found.');
        let response;
        if (typeof this.#continuation === 'string') {
            response = await this.#actions.execute('/browse', {
                client: 'YTMUSIC',
                continuation: this.#continuation
            });
        }
        else {
            response = await this.#continuation.endpoint.call(this.#actions, { client: 'YTMUSIC' });
        }
        return new Playlist(response, this.#actions);
    }
    /**
     * Retrieves related playlists
     */
    async getRelated() {
        const target_section_list = this.#page.contents_memo?.getType(SectionList).find((section_list) => section_list.continuation);
        if (!target_section_list)
            throw new InnertubeError('Could not find "Related" section.');
        let section_continuation = target_section_list.continuation;
        while (section_continuation) {
            const data = await this.#actions.execute('/browse', {
                client: 'YTMUSIC',
                continuation: section_continuation,
                parse: true
            });
            const section_list = data.continuation_contents?.as(SectionListContinuation);
            const sections = section_list?.contents?.as(MusicCarouselShelf, MusicShelf);
            const related = sections?.find((section) => section.is(MusicCarouselShelf))?.as(MusicCarouselShelf);
            if (related)
                return related;
            section_continuation = section_list?.continuation;
        }
        throw new InnertubeError('Could not fetch related playlists.');
    }
    async getSuggestions(refresh = true) {
        const require_fetch = refresh || !this.#last_fetched_suggestions;
        const fetch_promise = require_fetch ? this.#fetchSuggestions() : Promise.resolve(null);
        const fetch_result = await fetch_promise;
        if (fetch_result) {
            this.#last_fetched_suggestions = fetch_result.items;
            this.#suggestions_continuation = fetch_result.continuation;
        }
        return fetch_result?.items || this.#last_fetched_suggestions || observe([]);
    }
    async #fetchSuggestions() {
        const target_section_list = this.#page.contents_memo?.getType(SectionList).find((section_list) => section_list.continuation);
        const continuation = this.#suggestions_continuation || target_section_list?.continuation;
        if (continuation) {
            const page = await this.#actions.execute('/browse', {
                client: 'YTMUSIC',
                continuation: continuation,
                parse: true
            });
            const section_list = page.continuation_contents?.as(SectionListContinuation);
            const sections = section_list?.contents?.as(MusicCarouselShelf, MusicShelf);
            const suggestions = sections?.find((section) => section.is(MusicShelf))?.as(MusicShelf);
            return {
                items: suggestions?.contents || observe([]),
                continuation: suggestions?.continuation || null
            };
        }
        return {
            items: observe([]),
            continuation: null
        };
    }
    get page() {
        return this.#page;
    }
    get items() {
        return this.contents || observe([]);
    }
    get has_continuation() {
        return !!this.#continuation;
    }
}
//# sourceMappingURL=Playlist.js.map