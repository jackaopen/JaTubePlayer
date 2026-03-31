import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ContentMetadataView from './ContentMetadataView.js';
import AvatarStackView from './AvatarStackView.js';
import DecoratedAvatarView from './DecoratedAvatarView.js';
import Text from './misc/Text.js';
import ButtonView from './ButtonView.js';
export default class LockupMetadataView extends YTNode {
    static type = 'LockupMetadataView';
    title;
    metadata;
    image;
    menu_button;
    constructor(data) {
        super();
        this.title = Text.fromAttributed(data.title);
        this.metadata = Parser.parseItem(data.metadata, ContentMetadataView);
        this.image = Parser.parseItem(data.image, [DecoratedAvatarView, AvatarStackView]);
        this.menu_button = Parser.parseItem(data.menuButton, ButtonView);
    }
}
//# sourceMappingURL=LockupMetadataView.js.map