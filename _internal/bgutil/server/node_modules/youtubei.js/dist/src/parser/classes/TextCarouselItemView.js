import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import { Text } from '../misc.js';
import ButtonView from './ButtonView.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class TextCarouselItemView extends YTNode {
    static type = 'TextCarouselItemView';
    icon_name;
    text;
    on_tap_endpoint;
    button;
    constructor(data) {
        super();
        this.icon_name = data.iconName;
        this.text = Text.fromAttributed(data.text);
        this.on_tap_endpoint = new NavigationEndpoint(data.onTap);
        this.button = Parser.parseItem(data.button, ButtonView);
    }
}
//# sourceMappingURL=TextCarouselItemView.js.map