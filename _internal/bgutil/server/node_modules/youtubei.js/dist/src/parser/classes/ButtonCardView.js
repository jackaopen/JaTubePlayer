import { YTNode } from '../helpers.js';
import RendererContext from './misc/RendererContext.js';
export default class ButtonCardView extends YTNode {
    static type = 'ButtonCardView';
    title;
    icon_name;
    renderer_context;
    constructor(data) {
        super();
        this.title = data.title;
        this.icon_name = data.image.sources[0].clientResource.imageName;
        this.renderer_context = new RendererContext(data.rendererContext);
    }
}
//# sourceMappingURL=ButtonCardView.js.map