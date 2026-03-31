import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Menu from './menus/Menu.js';
import Author from './misc/Author.js';
import Text from './misc/Text.js';
export default class TwoColumnWatchNextResults extends YTNode {
    static type = 'TwoColumnWatchNextResults';
    results;
    secondary_results;
    conversation_bar;
    playlist;
    autoplay;
    constructor(data) {
        super();
        this.results = Parser.parseArray(data.results?.results.contents);
        this.secondary_results = Parser.parseArray(data.secondaryResults?.secondaryResults.results);
        this.conversation_bar = Parser.parseItem(data?.conversationBar);
        const playlistData = data.playlist?.playlist;
        if (playlistData) {
            this.playlist = {
                id: playlistData.playlistId,
                title: playlistData.title,
                author: playlistData.shortBylineText?.simpleText ?
                    new Text(playlistData.shortBylineText) :
                    new Author(playlistData.longBylineText),
                contents: Parser.parseArray(playlistData.contents),
                current_index: playlistData.currentIndex,
                is_infinite: !!playlistData.isInfinite,
                menu: Parser.parseItem(playlistData.menu, Menu)
            };
        }
        const autoplayData = data.autoplay?.autoplay;
        if (autoplayData) {
            this.autoplay = {
                sets: autoplayData.sets.map((set) => this.#parseAutoplaySet(set))
            };
            if (autoplayData.modifiedSets) {
                this.autoplay.modified_sets = autoplayData.modifiedSets.map((set) => this.#parseAutoplaySet(set));
            }
            if (autoplayData.countDownSecs) {
                this.autoplay.count_down_secs = autoplayData.countDownSecs;
            }
        }
    }
    #parseAutoplaySet(data) {
        const result = {
            autoplay_video: new NavigationEndpoint(data.autoplayVideo)
        };
        if (data.nextButtonVideo) {
            result.next_button_video = new NavigationEndpoint(data.nextButtonVideo);
        }
        return result;
    }
}
//# sourceMappingURL=TwoColumnWatchNextResults.js.map