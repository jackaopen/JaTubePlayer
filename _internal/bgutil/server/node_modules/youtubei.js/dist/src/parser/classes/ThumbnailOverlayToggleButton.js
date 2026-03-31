import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class ThumbnailOverlayToggleButton extends YTNode {
    static type = 'ThumbnailOverlayToggleButton';
    is_toggled;
    icon_type;
    tooltip;
    toggled_endpoint;
    untoggled_endpoint;
    constructor(data) {
        super();
        if (Reflect.has(data, 'isToggled')) {
            this.is_toggled = data.isToggled;
        }
        this.icon_type = {
            toggled: data.toggledIcon.iconType,
            untoggled: data.untoggledIcon.iconType
        };
        this.tooltip = {
            toggled: data.toggledTooltip,
            untoggled: data.untoggledTooltip
        };
        if (data.toggledServiceEndpoint)
            this.toggled_endpoint = new NavigationEndpoint(data.toggledServiceEndpoint);
        if (data.untoggledServiceEndpoint)
            this.untoggled_endpoint = new NavigationEndpoint(data.untoggledServiceEndpoint);
    }
}
//# sourceMappingURL=ThumbnailOverlayToggleButton.js.map