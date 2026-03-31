import GuideEntry from './GuideEntry.js';
export default class GuideDownloadsEntry extends GuideEntry {
    static type = 'GuideDownloadsEntry';
    always_show;
    constructor(data) {
        super(data.entryRenderer.guideEntryRenderer);
        this.always_show = !!data.alwaysShow;
    }
}
//# sourceMappingURL=GuideDownloadsEntry.js.map