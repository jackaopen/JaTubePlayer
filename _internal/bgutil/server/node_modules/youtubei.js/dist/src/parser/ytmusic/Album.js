import { Parser } from '../index.js';
import MicroformatData from '../classes/MicroformatData.js';
import MusicCarouselShelf from '../classes/MusicCarouselShelf.js';
import MusicDetailHeader from '../classes/MusicDetailHeader.js';
import MusicResponsiveHeader from '../classes/MusicResponsiveHeader.js';
import MusicShelf from '../classes/MusicShelf.js';
import { observe } from '../helpers.js';
export default class Album {
    #page;
    header;
    contents;
    sections;
    background;
    url;
    constructor(response) {
        this.#page = Parser.parseResponse(response.data);
        if (!this.#page.contents_memo)
            throw new Error('No contents found in the response');
        this.header = this.#page.contents_memo.getType(MusicDetailHeader, MusicResponsiveHeader)?.[0];
        this.contents = this.#page.contents_memo.getType(MusicShelf)?.[0].contents || observe([]);
        this.sections = this.#page.contents_memo.getType(MusicCarouselShelf) || observe([]);
        this.background = this.#page.background;
        this.url = this.#page.microformat?.as(MicroformatData).url_canonical;
    }
    get page() {
        return this.#page;
    }
}
//# sourceMappingURL=Album.js.map