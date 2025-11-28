"""
Email notification service for Padel Watcher
Sends email notifications when courts are found for search orders
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import (
    FRONTEND_BASE_URL,
    GMAIL_AUTH_CODE,
    GMAIL_SENDER_EMAIL,
    GMAIL_SENDER_EMAIL_NAME,
    GMAIL_SMTP_PORT,
    GMAIL_SMTP_SERVER,
)

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications"""

    def __init__(self):
        self.smtp_server = GMAIL_SMTP_SERVER
        self.smtp_port = GMAIL_SMTP_PORT
        self.sender_email = GMAIL_SENDER_EMAIL
        self.sender_name = GMAIL_SENDER_EMAIL_NAME
        self.auth_code = GMAIL_AUTH_CODE
        self.frontend_base_url = FRONTEND_BASE_URL

    def send_court_found_notification(
        self,
        recipient_email: str,
        recipient_name: str,
        search_order_id: int,
        courts_found: list[dict],
        search_params: dict,
    ) -> bool:
        """
        Send email notification when courts are found for a search order.

        Args:
            recipient_email: Email address to send to
            recipient_name: Name of the recipient
            search_order_id: ID of the search order
            courts_found: List of court availability results
            search_params: Search parameters (date, time, locations, etc.)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "🎾 Courts Found! - Padel Watcher Alert"
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = recipient_email

            # Create email body
            html_body = self._create_html_email(
                recipient_name, search_order_id, courts_found, search_params
            )
            text_body = self._create_text_email(
                recipient_name, search_order_id, courts_found, search_params
            )

            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            message.attach(part1)
            message.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.auth_code)
                server.sendmail(self.sender_email, recipient_email, message.as_string())

            logger.info(
                f"Email notification sent to {recipient_email} for search order {search_order_id}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to send email notification to {recipient_email}: {str(e)}"
            )
            return False

    def _create_text_email(
        self,
        recipient_name: str,
        search_order_id: int,
        courts_found: list[dict],
        search_params: dict,
    ) -> str:
        """Create plain text version of the email"""
        locations = ", ".join(search_params.get("locations", ["Unknown"]))

        text = f"""
Hi {recipient_name},

Great news! We found {len(courts_found)} available court(s) matching your search order #{search_order_id}.

Search Details:
- Date: {search_params.get('date', 'N/A')}
- Time: {search_params.get('start_time', 'N/A')} - {search_params.get('end_time', 'N/A')}
- Duration: {search_params.get('duration_minutes', 'N/A')} minutes
- Locations: {locations}
- Court Type: {search_params.get('court_type', 'all')}
- Configuration: {search_params.get('court_config', 'all')}

Available Courts:
"""

        for i, court in enumerate(courts_found, 1):
            text += f"""
{i}. {court.get('location', 'Unknown Location')} - {court.get('court', 'Unknown Court')}
   Time: {court.get('timeslot', 'N/A')}
   Price: {court.get('price', 'N/A')}
"""

        text += """
Book your court quickly before it's taken!

View all available courts: {search_url}

Best regards,
Padel Watcher Team
""".format(
            search_url=search_params.get("search_url", "N/A")
        )

        return text

    def _create_html_email(
        self,
        recipient_name: str,
        search_order_id: int,
        courts_found: list[dict],
        search_params: dict,
    ) -> str:
        """Create HTML version of the email"""
        locations = ", ".join(search_params.get("locations", ["Unknown"]))

        courts_html = ""
        for court in courts_found:
            booking_url = court.get("booking_url")
            booking_button = ""
            if booking_url:
                booking_button = f"""
                <a href="{booking_url}"
                   style="display: inline-block;
                          background-color: #059669;
                          color: white;
                          padding: 6px 12px;
                          text-decoration: none;
                          border-radius: 4px;
                          font-size: 12px;
                          font-weight: 600;">
                    Book Now
                </a>
                """

            courts_html += f"""
            <tr style="border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 12px; font-weight: 500;">{court.get('location', 'Unknown')}</td>
                <td style="padding: 12px;">{court.get('court', 'Unknown Court')}</td>
                <td style="padding: 12px;">{court.get('timeslot', 'N/A')}</td>
                <td style="padding: 12px; font-weight: 600; color: #059669;">{court.get('price', 'N/A')}</td>
                <td style="padding: 12px; text-align: center;">{booking_button}</td>
            </tr>
            """

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #374151; margin: 0; padding: 0; background-color: #f3f4f6;">
    <div style="max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px; font-weight: 700;">🎾 Courts Found!</h1>
            <p style="margin: 8px 0 0 0; font-size: 16px; opacity: 0.9;">Your Padel Watcher Alert</p>
        </div>

        <!-- Content -->
        <div style="padding: 30px;">
            <p style="font-size: 16px; margin: 0 0 20px 0;">Hi <strong>{recipient_name}</strong>,</p>

            <p style="font-size: 16px; margin: 0 0 20px 0;">Great news! We found <strong style="color: #059669;">{len(courts_found)} available court(s)</strong> matching your search order <strong>#{search_order_id}</strong>.</p>

            <!-- Search Details -->
            <div style="background-color: #f9fafb; border-left: 4px solid #059669; padding: 16px; margin: 20px 0; border-radius: 4px;">
                <h3 style="margin: 0 0 12px 0; font-size: 16px; color: #111827;">Search Details</h3>
                <table style="width: 100%; font-size: 14px;">
                    <tr>
                        <td style="padding: 4px 0; color: #6b7280;">Date:</td>
                        <td style="padding: 4px 0; font-weight: 600;">{search_params.get('date', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; color: #6b7280;">Time:</td>
                        <td style="padding: 4px 0; font-weight: 600;">{search_params.get('start_time', 'N/A')} - {search_params.get('end_time', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; color: #6b7280;">Duration:</td>
                        <td style="padding: 4px 0; font-weight: 600;">{search_params.get('duration_minutes', 'N/A')} minutes</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; color: #6b7280;">Locations:</td>
                        <td style="padding: 4px 0; font-weight: 600;">{locations}</td>
                    </tr>
                </table>
            </div>

            <!-- Available Courts -->
            <h3 style="margin: 24px 0 12px 0; font-size: 18px; color: #111827;">Available Courts</h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px; border: 1px solid #e5e7eb; border-radius: 4px;">
                <thead>
                    <tr style="background-color: #f9fafb;">
                        <th style="padding: 12px; text-align: left; font-weight: 600; color: #374151;">Location</th>
                        <th style="padding: 12px; text-align: left; font-weight: 600; color: #374151;">Court</th>
                        <th style="padding: 12px; text-align: left; font-weight: 600; color: #374151;">Time</th>
                        <th style="padding: 12px; text-align: left; font-weight: 600; color: #374151;">Price</th>
                        <th style="padding: 12px; text-align: center; font-weight: 600; color: #374151;">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {courts_html}
                </tbody>
            </table>

            <!-- Call to Action -->
            <div style="margin: 30px 0; padding: 20px; background-color: #fef3c7; border-radius: 4px; text-align: center;">
                <p style="margin: 0; font-size: 15px; color: #92400e;">
                    ⚡ <strong>Book quickly!</strong> Courts are filling up fast.
                </p>
            </div>

            <!-- View All Courts Button -->
            <div style="margin: 30px 0; text-align: center;">
                <a href="{search_params.get('search_url', '#')}"
                   style="background: linear-gradient(135deg, #059669 0%, #047857 100%);
                          color: white;
                          padding: 14px 28px;
                          text-decoration: none;
                          border-radius: 6px;
                          font-weight: 600;
                          font-size: 16px;
                          display: inline-block;
                          box-shadow: 0 2px 4px rgba(5, 150, 105, 0.3);">
                    🔍 View All Available Courts
                </a>
                <p style="margin: 12px 0 0 0; font-size: 12px; color: #6b7280;">
                    Click to see all courts matching your search criteria
                </p>
            </div>
        </div>

        <!-- Footer -->
        <div style="background-color: #f9fafb; padding: 20px; text-align: center; font-size: 12px; color: #6b7280;">
            <p style="margin: 0 0 8px 0;">You received this email because you have an active search order on Padel Watcher.</p>
            <p style="margin: 0;">To manage your search orders, log in to your account.</p>
        </div>
    </div>
</body>
</html>
"""

        return html


# Global email service instance
email_service = EmailService()
