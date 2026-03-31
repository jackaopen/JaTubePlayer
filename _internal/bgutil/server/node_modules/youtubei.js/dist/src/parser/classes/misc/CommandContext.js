import NavigationEndpoint from '../NavigationEndpoint.js';
export default class CommandContext {
    on_focus;
    on_hidden;
    on_touch_end;
    on_touch_move;
    on_long_press;
    on_tap;
    on_touch_start;
    on_visible;
    on_first_visible;
    on_hover;
    constructor(data) {
        if ('onFocus' in data)
            this.on_focus = new NavigationEndpoint(data.onFocus);
        if ('onHidden' in data)
            this.on_hidden = new NavigationEndpoint(data.onHidden);
        if ('onTouchEnd' in data)
            this.on_touch_end = new NavigationEndpoint(data.onTouchEnd);
        if ('onTouchMove' in data)
            this.on_touch_move = new NavigationEndpoint(data.onTouchMove);
        if ('onLongPress' in data)
            this.on_long_press = new NavigationEndpoint(data.onLongPress);
        if ('onTap' in data)
            this.on_tap = new NavigationEndpoint(data.onTap);
        if ('onTouchStart' in data)
            this.on_touch_start = new NavigationEndpoint(data.onTouchStart);
        if ('onVisible' in data)
            this.on_visible = new NavigationEndpoint(data.onVisible);
        if ('onFirstVisible' in data)
            this.on_first_visible = new NavigationEndpoint(data.onFirstVisible);
        if ('onHover' in data)
            this.on_hover = new NavigationEndpoint(data.onHover);
    }
}
//# sourceMappingURL=CommandContext.js.map