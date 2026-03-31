import { Parser } from '../index.js';
import Text from './misc/Text.js';
import Button from './Button.js';
import VideoOwner from './VideoOwner.js';
import SubscribeButton from './SubscribeButton.js';
import MetadataRowContainer from './MetadataRowContainer.js';
import { YTNode } from '../helpers.js';
export default class VideoSecondaryInfo extends YTNode {
    static type = 'VideoSecondaryInfo';
    owner;
    description;
    description_placeholder;
    subscribe_button;
    metadata;
    show_more_text;
    show_less_text;
    default_expanded;
    description_collapsed_lines;
    constructor(data) {
        super();
        this.owner = Parser.parseItem(data.owner, VideoOwner);
        this.description = new Text(data.description);
        if ('attributedDescription' in data)
            this.description = Text.fromAttributed(data.attributedDescription);
        if ('descriptionPlaceholder' in data)
            this.description_placeholder = new Text(data.descriptionPlaceholder);
        this.subscribe_button = Parser.parseItem(data.subscribeButton, [SubscribeButton, Button]);
        this.metadata = Parser.parseItem(data.metadataRowContainer, MetadataRowContainer);
        this.show_more_text = new Text(data.showMoreText);
        this.show_less_text = new Text(data.showLessText);
        this.default_expanded = data.defaultExpanded;
        this.description_collapsed_lines = data.descriptionCollapsedLines;
    }
}
//# sourceMappingURL=VideoSecondaryInfo.js.map