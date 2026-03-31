import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import AvatarView from './AvatarView.js';
import RendererContext from './misc/RendererContext.js';
export default class DecoratedAvatarView extends YTNode {
    static type = 'DecoratedAvatarView';
    avatar;
    a11y_label;
    renderer_context;
    constructor(data) {
        super();
        this.avatar = Parser.parseItem(data.avatar, AvatarView);
        this.a11y_label = data.a11yLabel;
        this.renderer_context = new RendererContext(data.rendererContext);
    }
}
//# sourceMappingURL=DecoratedAvatarView.js.map