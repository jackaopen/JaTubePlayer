import { YTNode } from '../helpers.js';
export default class ThumbnailBadgeView extends YTNode {
    static type = 'ThumbnailBadgeView';
    icon_name;
    text;
    badge_style;
    background_color;
    constructor(data) {
        super();
        this.text = data.text;
        this.badge_style = data.badgeStyle;
        if (data.backgroundColor) {
            this.background_color = {
                light_theme: data.backgroundColor.lightTheme,
                dark_theme: data.backgroundColor.darkTheme
            };
        }
        if (data.iconName) {
            this.icon_name = data.icon.sources[0].clientResource.imageName;
        }
    }
}
//# sourceMappingURL=ThumbnailBadgeView.js.map