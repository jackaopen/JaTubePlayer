import { YTNode } from '../helpers.js';
import { type RawNode } from '../index.js';
import DialogHeaderView from './DialogHeaderView.js';
import FormFooterView from './FormFooterView.js';
import CreatePlaylistDialogFormView from './CreatePlaylistDialogFormView.js';
import ListView from './ListView.js';
import PanelFooterView from './PanelFooterView.js';
export default class DialogView extends YTNode {
    static type: string;
    header: DialogHeaderView | null;
    footer: FormFooterView | PanelFooterView | null;
    custom_content: CreatePlaylistDialogFormView | ListView | null;
    constructor(data: RawNode);
}
