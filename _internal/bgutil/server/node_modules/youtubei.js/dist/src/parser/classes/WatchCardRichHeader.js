import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Author from './misc/Author.js';
import Text from './misc/Text.js';
export default class WatchCardRichHeader extends YTNode {
    static type = 'WatchCardRichHeader';
    title;
    title_endpoint;
    subtitle;
    author;
    style;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.title_endpoint = new NavigationEndpoint(data.titleNavigationEndpoint);
        this.subtitle = new Text(data.subtitle);
        this.author = new Author(data, data.titleBadge ? [data.titleBadge] : null, data.avatar);
        this.author.name = this.title.toString();
        this.style = data.style;
    }
}
//# sourceMappingURL=WatchCardRichHeader.js.map