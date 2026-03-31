import { YTNode } from '../helpers.js';
import { type RawNode } from '../index.js';
import ContentMetadataView from './ContentMetadataView.js';
import AvatarStackView from './AvatarStackView.js';
import DecoratedAvatarView from './DecoratedAvatarView.js';
import Text from './misc/Text.js';
import ButtonView from './ButtonView.js';
export default class LockupMetadataView extends YTNode {
    static type: string;
    title: Text;
    metadata: ContentMetadataView | null;
    image: DecoratedAvatarView | AvatarStackView | null;
    menu_button: ButtonView | null;
    constructor(data: RawNode);
}
