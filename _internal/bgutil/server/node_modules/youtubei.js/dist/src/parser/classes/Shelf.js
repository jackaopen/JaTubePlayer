import Text from './misc/Text.js';
import { Parser } from '../index.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
import Button from './Button.js';
export default class Shelf extends YTNode {
    static type = 'Shelf';
    title;
    endpoint;
    content;
    icon_type;
    menu;
    play_all_button;
    subtitle;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        if (Reflect.has(data, 'endpoint')) {
            this.endpoint = new NavigationEndpoint(data.endpoint);
        }
        this.content = Parser.parseItem(data.content);
        if (Reflect.has(data, 'icon')) {
            this.icon_type = data.icon.iconType;
        }
        if (Reflect.has(data, 'menu')) {
            this.menu = Parser.parseItem(data.menu);
        }
        if (Reflect.has(data, 'playAllButton')) {
            this.play_all_button = Parser.parseItem(data.playAllButton, Button);
        }
        if (Reflect.has(data, 'subtitle')) {
            this.subtitle = new Text(data.subtitle);
        }
    }
}
//# sourceMappingURL=Shelf.js.map