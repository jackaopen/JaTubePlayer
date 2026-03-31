import Text from './Text.js';
export default class SubscriptionButton {
    static type = 'SubscriptionButton';
    text;
    subscribed;
    subscription_type;
    constructor(data) {
        this.text = new Text(data.text);
        this.subscribed = data.isSubscribed;
        if ('subscriptionType' in data)
            this.subscription_type = data.subscriptionType;
    }
}
//# sourceMappingURL=SubscriptionButton.js.map