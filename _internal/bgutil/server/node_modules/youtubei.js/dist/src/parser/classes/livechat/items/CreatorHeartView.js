import { YTNode } from '../../../helpers.js';
import Thumbnail from '../../misc/Thumbnail.js';
export default class CreatorHeartView extends YTNode {
    static type = 'CreatorHeartView';
    creator_thumbnail;
    hearted_icon_name;
    unhearted_icon_name;
    unhearted_icon_processor;
    hearted_hover_text;
    hearted_accessibility_label;
    unhearted_accessibility_label;
    engagement_state_key;
    constructor(data) {
        super();
        this.creator_thumbnail = Thumbnail.fromResponse(data.creatorThumbnail);
        this.hearted_icon_name = data.heartedIcon.sources[0].clientResource.imageName;
        this.unhearted_icon_name = data.unheartedIcon.sources[0].clientResource.imageName;
        this.unhearted_icon_processor = {
            border_image_processor: {
                image_tint: {
                    color: data.unheartedIcon.processor.borderImageProcessor.imageTint.color
                }
            }
        };
        this.hearted_hover_text = data.heartedHoverText;
        this.hearted_accessibility_label = data.heartedAccessibilityLabel;
        this.unhearted_accessibility_label = data.unheartedAccessibilityLabel;
        this.engagement_state_key = data.engagementStateKey;
    }
}
//# sourceMappingURL=CreatorHeartView.js.map