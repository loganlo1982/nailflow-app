// (lệnh 581) A customer's text looks like iMessage: the round picture (the customer's first letter on their own colour – or a photo later),
// the name in bold (no name → the number), the words under it, NailFlow's small icon on the corner of the picture, one group per customer,
// tap → that chat. The server sends aps.mutable-content = 1 and "nf" = {chat, sender, initial, color, thread, url}.
// Anything missing / any error → the notification is shown exactly as it came (never lost).
import UserNotifications
import Intents
import UIKit

class NotificationService: UNNotificationServiceExtension {
    var contentHandler: ((UNNotificationContent) -> Void)?
    var bestAttempt: UNMutableNotificationContent?

    override func didReceive(_ request: UNNotificationRequest, withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void) {
        self.contentHandler = contentHandler
        let best = (request.content.mutableCopy() as? UNMutableNotificationContent) ?? UNMutableNotificationContent()
        bestAttempt = best
        guard let nf = request.content.userInfo["nf"] as? [String: Any], (nf["chat"] as? String) == "1" else { contentHandler(best); return }
        let name = (nf["sender"] as? String).flatMap { $0.isEmpty ? nil : $0 } ?? best.title
        let initial = (nf["initial"] as? String) ?? String(name.prefix(1))
        let color = (nf["color"] as? String) ?? "#8E8E93"
        let thread = (nf["thread"] as? String).flatMap { $0.isEmpty ? nil : $0 } ?? best.threadIdentifier
        if !thread.isEmpty { best.threadIdentifier = thread }
        let handle = INPersonHandle(value: thread.isEmpty ? name : thread, type: .unknown)
        let image = Self.avatar(initial: initial, hex: color).flatMap { $0.pngData() }.map { INImage(imageData: $0) }
        let sender = INPerson(personHandle: handle, nameComponents: nil, displayName: name, image: image, contactIdentifier: nil, customIdentifier: thread.isEmpty ? name : thread)
        let intent = INSendMessageIntent(recipients: nil, outgoingMessageType: .outgoingMessageText, content: best.body, speakableGroupName: nil,
                                         conversationIdentifier: thread.isEmpty ? nil : thread, serviceName: nil, sender: sender, attachments: nil)
        if let img = image { intent.setImage(img, forParameterNamed: \.sender) }
        let interaction = INInteraction(intent: intent, response: nil)
        interaction.direction = .incoming
        interaction.donate { _ in
            do {
                let updated = try best.updating(from: intent)
                contentHandler(updated)
            } catch {
                contentHandler(best)
            }
        }
    }

    override func serviceExtensionTimeWillExpire() {
        if let h = contentHandler, let b = bestAttempt { h(b) }
    }

    /// The first letter, white and bold, on a circle of the customer's colour (like Contacts).
    static func avatar(initial: String, hex: String) -> UIImage? {
        let size = CGSize(width: 120, height: 120)
        let col = color(hex) ?? UIColor.systemGray
        let r = UIGraphicsImageRenderer(size: size)
        return r.image { ctx in
            col.setFill()
            ctx.cgContext.fillEllipse(in: CGRect(origin: .zero, size: size))
            let s = String(initial.prefix(2)).uppercased() as NSString
            let attrs: [NSAttributedString.Key: Any] = [.font: UIFont.systemFont(ofSize: 54, weight: .bold), .foregroundColor: UIColor.white]
            let t = s.size(withAttributes: attrs)
            s.draw(at: CGPoint(x: (size.width - t.width) / 2, y: (size.height - t.height) / 2), withAttributes: attrs)
        }
    }
    static func color(_ hex: String) -> UIColor? {
        var h = hex.trimmingCharacters(in: .whitespaces); if h.hasPrefix("#") { h.removeFirst() }
        guard h.count == 6, let v = UInt32(h, radix: 16) else { return nil }
        return UIColor(red: CGFloat((v >> 16) & 0xFF) / 255, green: CGFloat((v >> 8) & 0xFF) / 255, blue: CGFloat(v & 0xFF) / 255, alpha: 1)
    }
}
