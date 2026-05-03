# ClamTk Refresh - Modern GUI Redesign
# copyright (C) 2004-2024 Dave M, Redesigned 2026
#
# This file is part of ClamTk
# https://github.com/dave-theunsub/clamtk/
# https://gitlab.com/dave_m/clamtk/
#
# ClamTk is free software; you can redistribute it and/or modify it
# under the terms of either:
#
# a) the GNU General Public License as published by the Free Software
# Foundation; either version 1, or (at your option) any later version, or
#
# b) the "Artistic License".
package ClamTk::GUI;

use Gtk3 '-init';
use Glib 'TRUE', 'FALSE';

$| = 1;

use POSIX 'locale_h';
use Locale::gettext;
use Cairo;

my $window;
my $infobar;
my $top_box;
my $box;
my $css_provider;

my $theme = Gtk3::IconTheme::get_default;
$theme->append_search_path( '/usr/share/icons/gnome/24x24/actions' );
$theme->append_search_path( '/usr/share/icons/gnome/24x24/places' );
$theme->append_search_path( '/usr/share/icons/gnome/24x24/mimetypes' );

my $modern_css = <<'CSS';
@define-color bg_color #f5f5f7;
@define-color card_color #ffffff;
@define-color accent_color #007aff;
@define-color accent_hover #0056b3;
@define-color text_primary #1d1d1f;
@define-color text_secondary #86868b;
@define-color border_color #d2d2d7;
@define-color success_color #34c759;
@define-color warning_color #ff9500;
@define-color danger_color #ff3b30;

window {
    background-color: @bg_color;
}

.header-bar {
    background: linear-gradient(to bottom, #ffffff, #f5f5f7);
    border-bottom: 1px solid @border_color;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.header-bar .title {
    font-weight: 600;
    font-size: 15px;
    color: @text_primary;
}

button {
    background: @card_color;
    border: 1px solid @border_color;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    color: @text_primary;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

button:hover {
    background: #fafafa;
    border-color: @accent_color;
}

button.suggested-action {
    background: @accent_color;
    color: white;
    border: none;
    font-weight: 600;
}

button.suggested-action:hover {
    background: @accent_hover;
}

.icon-view {
    background: transparent;
    border: none;
}

.icon-view .item {
    border-radius: 12px;
    padding: 12px;
    margin: 4px;
}

.icon-view .item:hover {
    background: rgba(0,122,255,0.08);
}

.icon-view .item:selected {
    background: rgba(0,122,255,0.15);
    border: 2px solid @accent_color;
}

.info-bar {
    border-radius: 8px;
    margin: 8px;
}

.card {
    background: @card_color;
    border: 1px solid @border_color;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.label-primary {
    font-weight: 600;
    font-size: 14px;
    color: @text_primary;
}

.label-secondary {
    font-size: 12px;
    color: @text_secondary;
}
CSS

sub start_gui {
    $window = Gtk3::Window->new( 'toplevel' );
    $window->signal_connect(
        destroy => sub {
            $window->destroy;
            Gtk3->main_quit;
            TRUE;
        }
    );
    $window->signal_connect(
        delete_event => sub {
            $window->destroy;
            Gtk3->main_quit;
        }
    );
    $window->set_default_size( 1100, 800 );
    $window->set_position( 'center' );

    $css_provider = Gtk3::CssProvider->new;
    $css_provider->load_from_data($modern_css);
    my $screen = $window->get_screen;
    Gtk3::StyleContext::add_provider_for_screen(
        $screen,
        $css_provider,
        Gtk3::STYLE_PROVIDER_PRIORITY_APPLICATION
    );

    my $hb = Gtk3::HeaderBar->new;
    $hb->set_show_close_button( TRUE );
    $hb->set_title( _( 'ClamTK Refresh' ) );
    $hb->set_subtitle( _( 'Modern Virus Scanner' ) );
    $window->set_titlebar( $hb );

    my $menu_button = Gtk3::MenuButton->new;
    my $menu_icon = Gtk3::Image->new_from_icon_name( 'open-menu-symbolic', 2 );
    $menu_button->set_image( $menu_icon );
    $hb->pack_end( $menu_button );

    my $help_button = Gtk3::Button->new_with_label( _( 'About' ) );
    $help_button->signal_connect( 'clicked', sub { about() } );
    $hb->pack_end( $help_button );

    my $main_box = Gtk3::Box->new( 'vertical', 0 );
    $window->add( $main_box );

    $infobar = Gtk3::InfoBar->new;
    $infobar->add_button( 'gtk-go-back', -5 );
    $infobar->signal_connect( 'response' => \&add_default_view );
    $main_box->pack_start( $infobar, FALSE, FALSE, 0 );

    my $infobar_label = Gtk3::Label->new( '' );
    $infobar_label->set_use_markup( TRUE );
    $infobar->get_content_area()->add( $infobar_label );

    my $scrolled_window = Gtk3::ScrolledWindow->new;
    $scrolled_window->set_policy( 'automatic', 'automatic' );
    $main_box->pack_start( $scrolled_window, TRUE, TRUE, 0 );

    $box = Gtk3::Box->new( 'vertical', 12 );
    $box->set_border_width( 16 );
    $scrolled_window->add_with_viewport( $box );

    my $ui_info = ClamTk::Shortcuts->get_ui_info;
    my @entries = ClamTk::Shortcuts->get_pseudo_keys;

    my $actions = Gtk3::ActionGroup->new( 'Actions' );
    $actions->add_actions( \@entries, undef );

    my $ui = Gtk3::UIManager->new;
    $ui->insert_action_group( $actions, 0 );

    $window->add_accel_group( $ui->get_accel_group );
    $ui->add_ui_from_string( $ui_info );

    add_default_view();
    startup();

    $window->show_all;
    Gtk3->main;
}

sub startup {
    Gtk3::main_iteration while Gtk3::events_pending;

    my $startup_check = ClamTk::Startup->startup_check();
    my ( $message_type, $message );
    if ( $startup_check eq 'both' ) {
        $message      = _( 'Updates are available' );
        $message_type = 'other';
    } elsif ( $startup_check eq 'sigs' ) {
        $message      = _( 'The antivirus signatures are outdated' );
        $message_type = 'warning';
    } elsif ( $startup_check eq 'gui' ) {
        $message      = _( 'An update is available' );
        $message_type = 'other';
    } else {
        $message      = '';
        $message_type = 'other';
    }
    Gtk3::main_iteration while Gtk3::events_pending;
    set_infobar_mode( $message_type, $message );
    $window->queue_draw;
    $infobar->show;
    $window->queue_draw;
}

sub set_infobar_mode {
    my ( $type, $text ) = @_;
    $infobar->set_message_type( $type );
    for my $c ( $infobar->get_content_area->get_children ) {
        if ( $c->isa( 'Gtk3::Label' ) ) {
            $c->set_text( $text );
        }
    }
}

sub set_infobar_text_remote {
    my ( $pkg, $type, $text ) = @_;
    $infobar->set_message_type( $type );
    for my $c ( $infobar->get_content_area->get_children ) {
        if ( $c->isa( 'Gtk3::Label' ) ) {
            $c->set_text( $text );
        }
    }
}

sub add_default_view {
    remove_box_children();

    my $hero_card = Gtk3::Box->new( 'vertical', 8 );
    $hero_card->set_border_width( 12 );
    my $hero_style = $hero_card->get_style_context;
    $hero_card->set_size_request( -1, 80 );

    my $hero_label = Gtk3::Label->new;
    $hero_label->set_markup( '<span size="18000" weight="bold" color="#1d1d1f">' . _( 'ClamTK Refresh' ) . '</span>' );
    $hero_label->set_halign( 'start' );
    $hero_card->pack_start( $hero_label, FALSE, FALSE, 0 );

    my $hero_sub = Gtk3::Label->new( _( 'Modern antivirus scanning for Linux' ) );
    $hero_sub->set_markup( '<span size="9000" color="#86868b">' . _( 'Modern antivirus scanning for Linux' ) . '</span>' );
    $hero_sub->set_halign( 'start' );
    $hero_card->pack_start( $hero_sub, FALSE, FALSE, 0 );

    $box->pack_start( $hero_card, FALSE, FALSE, 0 );

    my $scan_section = create_modern_section( _( 'Scan' ), _( 'Scan files and directories for threats' ) );
    my $scan_grid = Gtk3::Grid->new;
    $scan_grid->set_column_spacing( 8 );
    $scan_grid->set_row_spacing( 8 );
    $scan_grid->set_column_homogeneous( TRUE );
    $scan_section->add( $scan_grid );

    my $scan_file_btn = create_modern_action_card(
        _( 'Scan File' ),
        _( 'Scan a single file for viruses' ),
        'document-new',
        sub { select_file(); }
    );
    $scan_grid->attach( $scan_file_btn, 0, 0, 1, 1 );

    my $scan_dir_btn = create_modern_action_card(
        _( 'Scan Directory' ),
        _( 'Scan an entire directory recursively' ),
        'folder-documents',
        sub { select_directory(); }
    );
    $scan_grid->attach( $scan_dir_btn, 1, 0, 1, 1 );

    my $analysis_btn = create_modern_action_card(
        _( 'Analysis' ),
        _( "Check a file's reputation online" ),
        'system-search',
        sub { ClamTk::Analysis->show_window; }
    );
    $scan_grid->attach( $analysis_btn, 2, 0, 1, 1 );

    $box->pack_start( $scan_section, FALSE, FALSE, 0 );

    my $protect_section = create_modern_section( _( 'Protection' ), _( 'Manage quarantine and view history' ) );
    my $protect_grid = Gtk3::Grid->new;
    $protect_grid->set_column_spacing( 8 );
    $protect_grid->set_row_spacing( 8 );
    $protect_grid->set_column_homogeneous( TRUE );
    $protect_section->add( $protect_grid );

    my $history_btn = create_modern_action_card(
        _( 'History' ),
        _( 'View previous scan results' ),
        'view-list',
        sub {
            remove_box_children();
            swap_button( TRUE );
            $box->add( ClamTk::History->show_window );
            $window->queue_draw;
        }
    );
    $protect_grid->attach( $history_btn, 0, 0, 1, 1 );

    my $quarantine_btn = create_modern_action_card(
        _( 'Quarantine' ),
        _( 'Manage quarantined files' ),
        'user-trash-full',
        sub {
            remove_box_children();
            swap_button( TRUE );
            $box->add( ClamTk::Quarantine->show_window );
            $window->queue_draw;
        }
    );
    $protect_grid->attach( $quarantine_btn, 1, 0, 1, 1 );

    my $whitelist_btn = create_modern_action_card(
        _( 'Whitelist' ),
        _( 'Manage scanning exclusions' ),
        'security-high',
        sub {
            remove_box_children();
            swap_button( TRUE );
            $box->add( ClamTk::Whitelist->show_window );
            $window->queue_draw;
        }
    );
    $protect_grid->attach( $whitelist_btn, 2, 0, 1, 1 );

    $box->pack_start( $protect_section, FALSE, FALSE, 0 );

    my $settings_section = create_modern_section( _( 'Settings' ), _( 'Configure and update ClamTK' ) );
    my $settings_grid = Gtk3::Grid->new;
    $settings_grid->set_column_spacing( 8 );
    $settings_grid->set_row_spacing( 8 );
    $settings_grid->set_column_homogeneous( TRUE );
    $settings_section->add( $settings_grid );

    my $settings_btn = create_modern_action_card(
        _( 'Preferences' ),
        _( 'View and set your preferences' ),
        'preferences-system',
        sub {
            remove_box_children();
            swap_button( TRUE );
            $box->add( ClamTk::Settings->show_window );
            $window->queue_draw;
        }
    );
    $settings_grid->attach( $settings_btn, 0, 0, 1, 1 );

    my $update_btn = create_modern_action_card(
        _( 'Update' ),
        _( 'Update antivirus signatures' ),
        'software-update-available',
        sub {
            remove_box_children();
            swap_button( TRUE );
            $box->add( ClamTk::Update->show_window );
            $window->queue_draw;
        }
    );
    $settings_grid->attach( $update_btn, 1, 0, 1, 1 );

    my $network_btn = create_modern_action_card(
        _( 'Network' ),
        _( 'Configure proxy settings' ),
        'preferences-system-network',
        sub {
            remove_box_children();
            swap_button( TRUE );
            $box->add( ClamTk::Network->show_window );
            $window->queue_draw;
        }
    );
    $settings_grid->attach( $network_btn, 2, 0, 1, 1 );

    my $scheduler_btn = create_modern_action_card(
        _( 'Scheduler' ),
        _( 'Schedule scans and updates' ),
        'alarm',
        sub {
            ClamTk::Schedule->show_window( $window->get_position );
        }
    );
    $settings_grid->attach( $scheduler_btn, 3, 0, 1, 1 );

    $box->pack_start( $settings_section, FALSE, FALSE, 0 );

    my $assistant_btn = create_modern_action_card(
        _( 'Update Assistant' ),
        _( 'Signature update preferences' ),
        'system-help',
        sub {
            remove_box_children();
            swap_button( TRUE );
            $box->add( ClamTk::Assistant->show_window );
            $window->queue_draw;
        }
    );
    $settings_grid->attach( $assistant_btn, 4, 0, 1, 1 );

    $box->show_all;
    swap_button( FALSE );
    $window->queue_draw;
}

sub create_modern_section {
    my ( $title, $subtitle ) = @_;

    my $section = Gtk3::Box->new( 'vertical', 6 );
    $section->set_border_width( 6 );

    my $title_label = Gtk3::Label->new;
    $title_label->set_markup( '<span size="11000" weight="bold" color="#1d1d1f">' . $title . '</span>' );
    $title_label->set_halign( 'start' );
    $section->pack_start( $title_label, FALSE, FALSE, 0 );

    if ( $subtitle ) {
        my $sub_label = Gtk3::Label->new( $subtitle );
        $sub_label->set_markup( '<span size="10000" color="#86868b">' . $subtitle . '</span>' );
        $sub_label->set_halign( 'start' );
        $section->pack_start( $sub_label, FALSE, FALSE, 0 );
    }

    return $section;
}

sub create_modern_action_card {
    my ( $title, $description, $icon_name, $callback ) = @_;

    my $card = Gtk3::Button->new;
    $card->signal_connect( 'clicked', $callback );
    $card->set_relief( 'none' );
    $card->set_size_request( 150, 110 );

    my $card_box = Gtk3::Box->new( 'vertical', 6 );
    $card_box->set_border_width( 8 );
    $card->add( $card_box );

    my $icon = Gtk3::Image->new_from_icon_name( $icon_name, 4 );
    $icon->set_pixel_size( 36 );
    $icon->set_halign( 'center' );
    $card_box->pack_start( $icon, FALSE, FALSE, 0 );

    my $title_label = Gtk3::Label->new( $title );
    $title_label->set_markup( '<span weight="600" size="10000">' . $title . '</span>' );
    $title_label->set_halign( 'center' );
    $title_label->set_size_request( 130, -1 );
    $card_box->pack_start( $title_label, FALSE, FALSE, 0 );

    my $desc_label = Gtk3::Label->new( $description );
    $desc_label->set_markup( '<span size="8500" color="#86868b">' . $description . '</span>' );
    $desc_label->set_halign( 'center' );
    $desc_label->set_line_wrap( TRUE );
    $desc_label->set_max_width_chars( 16 );
    $desc_label->set_size_request( 130, -1 );
    $card_box->pack_start( $desc_label, FALSE, FALSE, 0 );

    return $card;
}

sub swap_button {
    my $change_to = shift;
    if ( $change_to ) {
        $infobar->add_button( 'gtk-go-back', -5 );
        $infobar->signal_connect(
            response => sub {
                my ( $package, $filename, $line ) = caller;
                add_default_view();
                if ( $package eq 'ClamTk::Update' ) {
                    startup();
                }
            }
        );
    } else {
        for my $a ( $infobar->get_action_area ) {
            for my $b ( $a->get_children ) {
                if ( $b->isa( 'Gtk3::Button' ) ) {
                    $b->destroy;
                }
            }
        }
    }
}

sub select_file {
    my $file   = '';
    my $dialog = Gtk3::FileChooserDialog->new(
        _( 'Select a file' ), $window,
        'open',
        'gtk-cancel' => 'cancel',
        'gtk-ok'     => 'ok',
    );
    $dialog->set_select_multiple( FALSE );
    $dialog->set_position( 'center-on-parent' );
    $dialog->set_show_hidden( FALSE );

    if ( 'ok' eq $dialog->run ) {
        $window->queue_draw;
        Gtk3::main_iteration while Gtk3::events_pending;
        $file = $dialog->get_filename;
        $dialog->destroy;
        $window->queue_draw;
    } else {
        $dialog->destroy;
        return FALSE;
    }

    if ( $file =~ m#^(/proc|/sys|/dev)# ) {
        ClamTk::Scan::popup(
            _( 'You do not have permissions to scan that file or directory' )
        );
        undef $file;
        select_file();
    }

    if ( -e $file ) {
        ClamTk::Scan->filter( $file, FALSE, undef );
    }
}

sub select_directory {
    my $directory = '';

    my $dialog = Gtk3::FileChooserDialog->new(
        _( 'Select a directory' ), $window,
        'select-folder',
        'gtk-cancel' => 'cancel',
        'gtk-ok'     => 'ok',
    );
    $dialog->set_position( 'center-on-parent' );
    $dialog->set_current_folder( ClamTk::App->get_path( 'directory' ) );
    $dialog->set_show_hidden( FALSE );

    if ( 'ok' eq $dialog->run ) {
        $directory = $dialog->get_filename;
        Gtk3::main_iteration while Gtk3::events_pending;
        $dialog->destroy;
        $window->queue_draw;
    } else {
        $dialog->destroy;
        return FALSE;
    }

    if ( $directory =~ m#^(/proc|/sys|/dev)# ) {
        ClamTk::Scan::popup(
            _( 'You do not have permissions to scan that file or directory' )
        );
        undef $directory;
        select_directory();
    }

    if ( -e $directory ) {
        ClamTk::Scan->filter( $directory, FALSE, undef );
    }
}

sub remove_box_children {
    for my $c ( $box->get_children ) {
        $box->remove( $c );
    }
}

sub about {
    my $dialog = Gtk3::AboutDialog->new;
    my $license
        = 'ClamTk Refresh is free software; you can redistribute it and/or'
        . ' modify it under the terms of either:'
        . ' a) the GNU General Public License as published by the Free'
        . ' Software Foundation; either version 1, or (at your option)'
        . ' any later version, or'
        . ' b) the "Artistic License".';
    $dialog->set_wrap_license( TRUE );
    $dialog->set_position( 'mouse' );

    my $images_dir = ClamTk::App->get_path( 'images' );
    my $icon       = "$images_dir/clamtk.png";
    my $pixbuf     = Gtk3::Gdk::Pixbuf->new_from_file( $icon );

    $dialog->set_logo( $pixbuf );
    $dialog->set_version( ClamTk::App->get_TK_version() . ' Refresh' );
    $dialog->set_license( $license );
    $dialog->set_website_label( _( 'Homepage' ) );
    $dialog->set_website( 'https://gitlab.com/dave_m/clamtk/wikis/Home' );
    $dialog->set_logo( $pixbuf );
    $dialog->set_translator_credits(
        'Please see the credits.md for full listing' );
    $dialog->set_copyright( "\x{a9} Dave M 2004 - 2024, Refresh 2026" );
    $dialog->set_program_name( 'ClamTK Refresh' );
    $dialog->set_authors( [ 'Dave M', 'dave.nerd@gmail.com', 'Refresh Design Team' ] );
    $dialog->set_comments(
              _( 'ClamTk Refresh - A modern graphical front-end for Clam Antivirus' ) . "\n"
            . '(ClamAV '
            . ClamTk::App->get_AV_version()
            . ')' );

    $dialog->run;
    $dialog->destroy;
}

1;
