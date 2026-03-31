import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
import Button from './Button.js';
import Menu from './menus/Menu.js';
import InfoPanelContainer from './InfoPanelContainer.js';
import LikeButton from './LikeButton.js';
import ReelPlayerHeader from './ReelPlayerHeader.js';
import PivotButton from './PivotButton.js';
import SubscribeButton from './SubscribeButton.js';
export default class ReelPlayerOverlay extends YTNode {
    static type = 'ReelPlayerOverlay';
    like_button;
    reel_player_header_supported_renderers;
    menu;
    next_item_button;
    prev_item_button;
    subscribe_button_renderer;
    style;
    view_comments_button;
    share_button;
    pivot_button;
    info_panel;
    constructor(data) {
        super();
        this.like_button = Parser.parseItem(data.likeButton, LikeButton);
        this.reel_player_header_supported_renderers = Parser.parseItem(data.reelPlayerHeaderSupportedRenderers, ReelPlayerHeader);
        this.menu = Parser.parseItem(data.menu, Menu);
        this.next_item_button = Parser.parseItem(data.nextItemButton, Button);
        this.prev_item_button = Parser.parseItem(data.prevItemButton, Button);
        this.subscribe_button_renderer = Parser.parseItem(data.subscribeButtonRenderer, [Button, SubscribeButton]);
        this.style = data.style;
        this.view_comments_button = Parser.parseItem(data.viewCommentsButton, Button);
        this.share_button = Parser.parseItem(data.shareButton, Button);
        this.pivot_button = Parser.parseItem(data.pivotButton, PivotButton);
        this.info_panel = Parser.parseItem(data.infoPanel, InfoPanelContainer);
    }
}
//# sourceMappingURL=ReelPlayerOverlay.js.map