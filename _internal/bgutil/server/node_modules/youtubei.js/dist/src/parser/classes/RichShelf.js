import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
export default class RichShelf extends YTNode {
    static type = 'RichShelf';
    title;
    contents;
    endpoint;
    subtitle;
    is_expanded;
    is_bottom_divider_hidden;
    is_top_divider_hidden;
    layout_sizing;
    icon_type;
    menu;
    next_button;
    previous_button;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.contents = Parser.parseArray(data.contents);
        this.is_expanded = !!data.is_expanded;
        this.is_bottom_divider_hidden = !!data.isBottomDividerHidden;
        this.is_top_divider_hidden = !!data.isTopDividerHidden;
        if ('endpoint' in data) {
            this.endpoint = new NavigationEndpoint(data.endpoint);
        }
        if ('subtitle' in data) {
            this.subtitle = new Text(data.subtitle);
        }
        if ('layoutSizing' in data) {
            this.layout_sizing = data.layoutSizing;
        }
        if ('icon' in data) {
            this.icon_type = data.icon.iconType;
        }
        this.menu = Parser.parseItem(data.menu);
        this.next_button = Parser.parseItem(data.nextButton);
        this.previous_button = Parser.parseItem(data.previousButton);
    }
}
//# sourceMappingURL=RichShelf.js.map