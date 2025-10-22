from src.domain.services import MailService
from src.data.mail.mailer import MailTransporter


class MailServiceImpl(MailService):
    def __init__(self, transporter: MailTransporter):
        self.transporter = transporter

    async def send_mail(self, to: str, subject: str, html: str):
        return await self.transporter.send_mail(to=to, subject=subject, html=html)

    def build_otp_template(self, otp: str) -> dict[str, str]:
        subject = "Mã xác thực OTP của bạn"

        html = f"""
            <div style="width:90%; background-color:#f0f2f3; padding:20px; border-radius:15px; font-family:Arial,sans-serif; color:#252f3d;">
                <div style="max-width:400px; margin:0 auto; background-color:#ffffff; border-radius:10px; padding:25px; box-shadow:0 4px 8px rgba(0,0,0,0.05);">
                    <h2 style="font-size:18px; color:#333; margin-bottom:20px;">Mã xác thực OTP của bạn</h2>

                    <p style="margin-bottom:15px; font-size:14px;">Người dùng thân mến,</p>
                    <p style="margin-bottom:15px; font-size:14px;">Dưới đây là mã OTP của bạn. Vui lòng không chia sẻ mã này với bất kỳ ai:</p>

                    <div style="color:#1d4ed8; font-size:20px; font-weight:bold; letter-spacing:2px; margin-bottom:20px; text-align:center;">
                        {otp}
                    </div>

                    <p style="font-size:13px; color:#555; margin-bottom:10px;">
                        Mã OTP này chỉ có hiệu lực trong 10 phút.
                    </p>
                    <p style="font-size:13px; color:#555; margin-bottom:10px;">
                        Đây là email tự động, vui lòng không trả lời.
                    </p>

                    <p style="font-size:12px; color:#555; margin-top:20px;">
                        Trân trọng,<br>
                        <strong>Cash Clever</strong>
                    </p>
                </div>
            </div>
            """

        return {"subject": subject, "html": html}
