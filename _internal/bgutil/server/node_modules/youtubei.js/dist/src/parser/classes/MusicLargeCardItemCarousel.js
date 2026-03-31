import NavigationEndpoint from './NavigationEndpoint.js';
import Thumbnail from './misc/Thumbnail.js';
import { YTNode } from '../helpers.js';
class ActionButton {
    static type = 'ActionButton';
    icon_name;
    endpoint;
    a11y_text;
    style;
    constructor(data) {
        this.icon_name = data.iconName;
        this.endpoint = new NavigationEndpoint(data.onTap);
        this.a11y_text = data.a11yText;
        this.style = data.style;
    }
}
class Panel {
    static type = 'Panel';
    image;
    content_mode;
    crop_options;
    image_aspect_ratio;
    caption;
    action_buttons;
    constructor(data) {
        this.image = Thumbnail.fromResponse(data.image.image);
        this.content_mode = data.image.contentMode;
        this.crop_options = data.image.cropOptions;
        this.image_aspect_ratio = data.imageAspectRatio;
        this.caption = data.caption;
        this.action_buttons = data.actionButtons.map((el) => new ActionButton(el));
    }
}
export default class MusicLargeCardItemCarousel extends YTNode {
    static type = 'MusicLargeCardItemCarousel';
    panels;
    header;
    constructor(data) {
        super();
        // TODO: check this
        this.header = data.shelf.header;
        this.panels = data.shelf.panels.map((el) => new Panel(el));
    }
}
//# sourceMappingURL=MusicLargeCardItemCarousel.js.map