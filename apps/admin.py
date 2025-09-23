#!/usr/bin/env python3
"""
Admin CLI for Vectorpenter user management
"""

import click
from core.auth import auth_manager, UserRole
from core.audit import audit_logger, AuditEventType
from core.logging import logger

@click.group()
def admin():
    """Vectorpenter Admin CLI"""
    pass

@admin.command()
@click.argument('username')
@click.option('--role', type=click.Choice(['admin', 'user', 'readonly']), default='user')
def create_user(username: str, role: str):
    """Create a new user and API key"""
    try:
        user_role = UserRole(role)
        api_key = auth_manager.create_user(username, user_role)
        
        click.echo(f"✅ User created successfully!")
        click.echo(f"Username: {username}")
        click.echo(f"Role: {role}")
        click.echo(f"API Key: {api_key}")
        click.echo(f"⚠️  Save this API key - it won't be shown again!")
        
        # Audit log
        audit_logger.log_user_action(
            AuditEventType.API_KEY_CREATED,
            username,
            details={"role": role, "created_by": "admin_cli"}
        )
        
    except ValueError as e:
        click.echo(f"❌ Error: {e}")
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        logger.exception("User creation failed")

@admin.command()
def list_users():
    """List all users"""
    users = auth_manager.users
    
    if not users:
        click.echo("No users found.")
        return
    
    click.echo(f"{'Username':<20} {'Role':<10} {'Created':<20} {'Last Active':<20}")
    click.echo("-" * 70)
    
    for username, user in users.items():
        import datetime
        created = datetime.datetime.fromtimestamp(user.created_at).strftime("%Y-%m-%d %H:%M")
        last_active = datetime.datetime.fromtimestamp(user.last_active).strftime("%Y-%m-%d %H:%M") if user.last_active > 0 else "Never"
        
        click.echo(f"{username:<20} {user.role.value:<10} {created:<20} {last_active:<20}")

@admin.command()
@click.argument('username')
@click.confirmation_option(prompt='Are you sure you want to delete this user?')
def delete_user(username: str):
    """Delete a user"""
    if username not in auth_manager.users:
        click.echo(f"❌ User {username} not found")
        return
    
    # Remove user and their API keys
    user = auth_manager.users[username]
    del auth_manager.users[username]
    
    # Remove API keys
    keys_to_remove = [key for key, user_name in auth_manager.api_keys.items() if user_name == username]
    for key in keys_to_remove:
        del auth_manager.api_keys[key]
    
    click.echo(f"✅ User {username} deleted successfully")
    
    # Audit log
    audit_logger.log_user_action(
        AuditEventType.API_KEY_REVOKED,
        username,
        details={"deleted_by": "admin_cli", "keys_revoked": len(keys_to_remove)}
    )

@admin.command()
@click.option('--lines', default=50, help='Number of recent log lines to show')
def audit_log(lines: int):
    """Show recent audit log entries"""
    try:
        from pathlib import Path
        audit_file = Path("logs/audit.log")
        
        if not audit_file.exists():
            click.echo("No audit log found")
            return
        
        # Read last N lines
        with open(audit_file, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        click.echo(f"Last {len(recent_lines)} audit log entries:")
        click.echo("-" * 80)
        
        for line in recent_lines:
            try:
                import json
                event = json.loads(line.strip())
                timestamp = datetime.datetime.fromtimestamp(event['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                event_type = event['event_type']
                user_id = event.get('user_id', 'unknown')
                success = event.get('success', True)
                status = "✅" if success else "❌"
                
                click.echo(f"{timestamp} {status} {event_type:<20} {user_id}")
                
            except Exception:
                click.echo(line.strip())  # Fallback to raw line
                
    except Exception as e:
        click.echo(f"❌ Error reading audit log: {e}")

@admin.command()
def health():
    """Check system health"""
    click.echo("🏥 Vectorpenter System Health")
    click.echo("-" * 40)
    
    # Check users
    user_count = len(auth_manager.users)
    click.echo(f"👥 Users: {user_count}")
    
    # Check services
    from core.validation import validate_environment
    config_status = validate_environment()
    
    for service, is_valid in config_status.items():
        status = "✅" if is_valid else "❌"
        click.echo(f"{status} {service}")
    
    # Overall health
    all_valid = all(config_status.values())
    overall_status = "🟢 Healthy" if all_valid else "🟡 Degraded"
    click.echo(f"\nOverall Status: {overall_status}")

if __name__ == "__main__":
    admin()
