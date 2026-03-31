import type { ObservedArray } from '../helpers.js';
import type { RawNode } from '../types/RawResponse.js';
import { YTNode } from '../helpers.js';
import AvatarView from './AvatarView.js';
import RendererContext from './misc/RendererContext.js';
import SubscribeButtonView from './SubscribeButtonView.js';
import Text from './misc/Text.js';
export default class ListItemView extends YTNode {
    static type: string;
    title: Text;
    subtitle: Text;
    leading_accessory: AvatarView | null;
    renderer_context: RendererContext;
    trailing_buttons?: ObservedArray<SubscribeButtonView>;
    constructor(data: RawNode);
}
