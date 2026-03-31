import { Parser } from '../index.js';
import { observe } from '../helpers.js';
import { InnertubeError } from '../../utils/Utils.js';
import MusicShelf from '../classes/MusicShelf.js';
import MusicCarouselShelf from '../classes/MusicCarouselShelf.js';
import MusicPlaylistShelf from '../classes/MusicPlaylistShelf.js';
import MusicImmersiveHeader from '../classes/MusicImmersiveHeader.js';
import MusicVisualHeader from '../classes/MusicVisualHeader.js';
import MusicHeader from '../classes/MusicHeader.js';
export default class Artist {
    #page;
    #actions;
    header;
    sections;
    constructor(response, actions) {
        this.#page = Parser.parseResponse(response.data);
        this.#actions = actions;
        this.header = this.page.header?.item().as(MusicImmersiveHeader, MusicVisualHeader, MusicHeader);
        const music_shelf = this.#page.contents_memo?.getType(MusicShelf) || [];
        const music_carousel_shelf = this.#page.contents_memo?.getType(MusicCarouselShelf) || [];
        this.sections = observe([...music_shelf, ...music_carousel_shelf]);
    }
    async getAllSongs() {
        const music_shelves = this.sections.filter((section) => section.type === 'MusicShelf');
        if (!music_shelves.length)
            throw new InnertubeError('Could not find any node of type MusicShelf.');
        const shelf = music_shelves.find((shelf) => shelf.title?.text === 'Top songs');
        if (!shelf)
            throw new InnertubeError('Could not find target shelf (Top songs).');
        if (!shelf.endpoint)
            throw new InnertubeError('Target shelf (Top songs) did not have an endpoint.');
        const page = await shelf.endpoint.call(this.#actions, { client: 'YTMUSIC', parse: true });
        return page.contents_memo?.getType(MusicPlaylistShelf)?.[0];
    }
    get page() {
        return this.#page;
    }
}
//# sourceMappingURL=Artist.js.map