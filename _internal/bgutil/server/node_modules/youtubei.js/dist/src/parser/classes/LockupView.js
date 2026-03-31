import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ThumbnailView from './ThumbnailView.js';
import CollectionThumbnailView from './CollectionThumbnailView.js';
import LockupMetadataView from './LockupMetadataView.js';
import RendererContext from './misc/RendererContext.js';
export default class LockupView extends YTNode {
    static type = 'LockupView';
    content_image;
    metadata;
    content_id;
    content_type;
    renderer_context;
    constructor(data) {
        super();
        this.content_image = Parser.parseItem(data.contentImage, [CollectionThumbnailView, ThumbnailView]);
        this.metadata = Parser.parseItem(data.metadata, LockupMetadataView);
        this.content_id = data.contentId;
        this.content_type = data.contentType.replace('LOCKUP_CONTENT_TYPE_', '');
        this.renderer_context = new RendererContext(data.rendererContext);
    }
}
//# sourceMappingURL=LockupView.js.map