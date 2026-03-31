import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ToggleButtonView from './ToggleButtonView.js';
export default class LikeButtonView extends YTNode {
    static type = 'LikeButtonView';
    toggle_button;
    like_status_entity_key;
    like_status_entity;
    constructor(data) {
        super();
        this.toggle_button = Parser.parseItem(data.toggleButtonViewModel, ToggleButtonView);
        this.like_status_entity_key = data.likeStatusEntityKey;
        this.like_status_entity = {
            key: data.likeStatusEntity.key,
            like_status: data.likeStatusEntity.likeStatus
        };
    }
}
//# sourceMappingURL=LikeButtonView.js.map