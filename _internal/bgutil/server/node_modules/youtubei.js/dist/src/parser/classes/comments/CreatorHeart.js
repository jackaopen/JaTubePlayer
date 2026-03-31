import { YTNode } from '../../helpers.js';
import Thumbnail from '../misc/Thumbnail.js';
export default class CreatorHeart extends YTNode {
    static type = 'CreatorHeart';
    creator_thumbnail;
    heart_icon_type;
    heart_color;
    hearted_tooltip;
    is_hearted;
    is_enabled;
    kennedy_heart_color_string;
    constructor(data) {
        super();
        this.creator_thumbnail = Thumbnail.fromResponse(data.creatorThumbnail);
        if (Reflect.has(data, 'heartIcon') && Reflect.has(data.heartIcon, 'iconType')) {
            this.heart_icon_type = data.heartIcon.iconType;
        }
        this.heart_color = {
            basic_color_palette_data: {
                foreground_title_color: data.heartColor?.basicColorPaletteData?.foregroundTitleColor
            }
        };
        this.hearted_tooltip = data.heartedTooltip;
        this.is_hearted = data.isHearted;
        this.is_enabled = data.isEnabled;
        this.kennedy_heart_color_string = data.kennedyHeartColorString;
    }
}
//# sourceMappingURL=CreatorHeart.js.map