import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import AvatarView from './AvatarView.js';
import RendererContext from './misc/RendererContext.js';
import SubscribeButtonView from './SubscribeButtonView.js';
import Text from './misc/Text.js';
export default class ListItemView extends YTNode {
    static type = 'ListItemView';
    title;
    subtitle;
    leading_accessory;
    renderer_context;
    trailing_buttons;
    constructor(data) {
        super();
        this.title = Text.fromAttributed(data.title);
        this.subtitle = Text.fromAttributed(data.subtitle);
        this.leading_accessory = Parser.parseItem(data.leadingAccessory, AvatarView);
        this.renderer_context = new RendererContext(data.rendererContext);
        if ('trailingButtons' in data) {
            this.trailing_buttons = Parser.parseArray(data.trailingButtons.buttons, SubscribeButtonView);
        }
    }
}
//# sourceMappingURL=ListItemView.js.map