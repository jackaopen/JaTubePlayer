import { YTNode } from '../helpers.js';
import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
export default class PivotButton extends YTNode {
    static type = 'PivotButton';
    thumbnail;
    endpoint;
    content_description;
    target_id;
    sound_attribution_title;
    waveform_animation_style;
    background_animation_style;
    constructor(data) {
        super();
        this.thumbnail = Thumbnail.fromResponse(data.thumbnail);
        this.endpoint = new NavigationEndpoint(data.onClickCommand);
        this.content_description = new Text(data.contentDescription);
        this.target_id = data.targetId;
        this.sound_attribution_title = new Text(data.soundAttributionTitle);
        this.waveform_animation_style = data.waveformAnimationStyle;
        this.background_animation_style = data.backgroundAnimationStyle;
    }
}
//# sourceMappingURL=PivotButton.js.map