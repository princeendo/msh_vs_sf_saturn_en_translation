! OPT-004: the EXTRA OPTIONS sub-menu of the Options screen.
!
! Assembled into the quote font's tail (EXP-0107) at a cart address set by
! the build. The Options menu is a state machine on STATE (EXP-0105); the
! sub-menu is its unused state 2:
!   - `entry` is the handler of Options row 8 (EXTRA OPTIONS). On A or C it
!     draws the sub-menu and sets STATE to 2, as BUTTON CONFIG does for 1;
!   - in state 2 the dispatcher calls 0x0601E22C, patched to jump to
!     `submenu`, every frame: Start leaves, up/down move, left/right change
!     the current row, and every row is redrawn.
! Calling convention (the game's): the caller pushes PR in the delay slot of
! its jsr/bsr, the callee pops it with `lds.l @r15+,pr` before `rts`.

        .equ STATE, 0x06017A84
        .equ PAD_PRESS, 0x0601A3F4      ! Start 0x0080, A or C 0x0560
        .equ PAD_DIR, 0x0601A3F8        ! up 1, down 2, left 4, right 8
        .equ COLOR_FLAG, 0x06017C0C
        .equ CLEAR, 0x0601AC28
        .equ PREPARE, 0x0601B6F0
        .equ BIG_TITLE, 0x0601B710
        .equ DRAW_VALUE, 0x0601E4EC
        .equ REDRAW_MAIN, 0x0601DDEC
        .equ SOUND_MOVE, 0x0601E3B6
        .equ SOUND_CHANGE, 0x0601E414
        .equ SOUND_ENTER, 0x0601E44A
        .equ SOUND_EXIT, 0x0601E474
        .equ EXIT_TEXT, 0x0601E8FE
        .equ ROWS, 2
        .equ ROW_SHIFT_NOTE, 32         ! bytes per row record (see `rows`)

! ---- Options row 8 handler: every frame the cursor is on EXTRA OPTIONS
entry:
        mov.l @(l_press),r1
        mov.l @r1,r1
        mov.l @(l_ac),r0
        and r1,r0
        tst r0,r0
        bt entry_done
        mov.l @(l_sound_enter),r0
        jsr @r0
        sts.l pr,@-r15
        bsr draw_screen
        sts.l pr,@-r15
        mov.l @(l_cursor),r1
        mov #0,r0
        mov.l r0,@r1
        mov.l @(l_state),r1
        mov #2,r0
        mov.l r0,@r1
entry_done:
        lds.l @r15+,pr
        rts
        nop

! ---- clear the screen; title, exit line
draw_screen:
        mov.l @(l_clear),r0
        jsr @r0
        sts.l pr,@-r15
        mov.l @(l_prepare),r0
        jsr @r0
        sts.l pr,@-r15
        mov.l @(l_title),r8
        mov.l @(l_color_flag),r0
        mov.b @r0,r0
        tst r0,r0
        bt title_chosen
        mov.l @(l_title_alt),r8
title_chosen:
        mov.b @r8+,r1
        mov.b @r8+,r2
        mov.b @r8+,r3
        mov.l @(l_big_title),r0
        jsr @r0
        sts.l pr,@-r15
        mov.l @(l_exit_text),r8
        trapa #48
        .word 0x0033
        lds.l @r15+,pr
        rts
        nop

! ---- state 2, every frame (jumped to from 0x0601E22C)
submenu:
        mov.l @(l_press),r1
        mov.l @r1,r1
        mov.l @(l_start),r0
        and r1,r0
        tst r0,r0
        bt stay
        mov.l @(l_redraw_main),r0       ! leave as BUTTON CONFIG does (0x0601E212)
        jsr @r0
        sts.l pr,@-r15
        mov.l @(l_sound_exit),r0
        jsr @r0
        sts.l pr,@-r15
        mov.l @(l_state),r1
        mov #0,r0
        mov.l r0,@r1
        lds.l @r15+,pr
        rts
        nop

stay:
        mov.l @(l_dir),r1
        mov.l @r1,r0
        mov.l @(l_dir_bits),r1
        mov.l r0,@r1                    ! this frame's direction bits
        and #3,r0
        tst r0,r0
        bt no_move
        mov.l @(l_cursor),r1
        mov.l @r1,r2
        cmp/eq #1,r0
        bf move_down
        add #-1,r2
        cmp/pz r2
        bt move_store
        bra move_store
        mov #ROWS-1,r2
move_down:
        cmp/eq #2,r0
        bf no_move
        add #1,r2
        mov #ROWS,r0
        cmp/ge r0,r2
        bf move_store
        mov #0,r2
move_store:
        mov.l r2,@r1
        mov.l @(l_sound_move),r0
        jsr @r0
        sts.l pr,@-r15

no_move:
        mov.l @(l_dir_bits),r1
        mov.l @r1,r0
        and #12,r0
        tst r0,r0
        bt draw
        mov r0,r5                       ! 4 = left, 8 = right
        bsr current_row
        sts.l pr,@-r15
        mov.l @r9,r8                    ! setting
        mov.l @(4,r9),r3                ! its maximum
        mov.l @r8,r2
        mov r5,r0
        cmp/eq #4,r0
        bf go_right
        add #-1,r2
        cmp/pz r2
        bt change_store
        bra change_store
        mov r3,r2
go_right:
        add #1,r2
        cmp/gt r3,r2
        bf change_store
        mov #0,r2
change_store:
        mov.l r2,@r8
        mov.l @(l_sound_change),r0
        jsr @r0
        sts.l pr,@-r15
        bsr current_row
        sts.l pr,@-r15
        mov.l @(8,r9),r0                ! the row's apply routine, if any
        tst r0,r0
        bt draw
        jsr @r0
        sts.l pr,@-r15

draw:
        mov.l @(l_row),r1
        mov #0,r0
        mov.l r0,@r1
draw_row:
        mov.l @(l_row),r1
        mov.l @r1,r4
        bsr row_at
        sts.l pr,@-r15
        ! label colours, as 0x0601E4EC picks them for values
        mov.l @(l_color_flag),r0
        mov.b @r0,r0
        tst r0,r0
        mov #104,r1
        bf/s colours
        mov #105,r2
        mov #0,r1
        mov #127,r2
colours:
        mov r1,r3
        mov.l @(l_cursor),r0
        mov.l @r0,r0
        cmp/eq r0,r4
        bf label
        mov r2,r3
label:
        mov.l @(12,r9),r8
        mov.b @r8+,r1
        mov.b @r8+,r2
        trapa #48
        .word 0x0032
        mov.l @(l_row),r1
        mov.l @r1,r4
        bsr row_at
        sts.l pr,@-r15
        mov.l @r9,r8                    ! setting
        mov.l @(16,r9),r9               ! value strings
        mov.l @(l_cursor),r10
        mov.l @(l_draw_value),r0
        jsr @r0
        sts.l pr,@-r15
        mov.l @(l_row),r1
        mov.l @r1,r0
        add #1,r0
        mov.l r0,@r1
        mov #ROWS,r1
        cmp/ge r1,r0
        bf draw_row
        lds.l @r15+,pr
        rts
        nop

! r9 = the record of the row under the cursor
current_row:
        mov.l @(l_cursor),r0
        mov.l @r0,r4
! r9 = the record of row r4 (32 bytes each)
row_at:
        mov r4,r0
        shll2 r0
        shll2 r0
        shll r0
        mov.l @(l_rows),r9
        add r0,r9
        lds.l @r15+,pr
        rts
        nop

        .align 4
l_press: .long PAD_PRESS
l_dir: .long PAD_DIR
l_ac: .long 0x0560
l_start: .long 0x0080
l_state: .long STATE
l_cursor: .long cursor
l_row: .long row
l_dir_bits: .long dir_bits
l_rows: .long rows
l_color_flag: .long COLOR_FLAG
l_clear: .long CLEAR
l_prepare: .long PREPARE
l_big_title: .long BIG_TITLE
l_title: .long title
l_title_alt: .long title_alt
l_exit_text: .long EXIT_TEXT
l_draw_value: .long DRAW_VALUE
l_redraw_main: .long REDRAW_MAIN
l_sound_move: .long SOUND_MOVE
l_sound_change: .long SOUND_CHANGE
l_sound_enter: .long SOUND_ENTER
l_sound_exit: .long SOUND_EXIT

! ---- variables (cart RAM is writable)
cursor: .long 0
row: .long 0
dir_bits: .long 0

! ---- rows: setting, maximum, apply routine (0 = none), label, value strings
rows:
        ! BOSS FIGHT: the title menu's boss fight unlock (OPT-001, EXP-0075)
        .long 0x06017AB0, 1, 0, label_boss, values_boss, 0, 0, 0
        ! COMBO GAUGE: the game's COMBO GAGE setting; 0x0601E172 applies it
        .long 0x06017AD4, 1, 0x0601E172, label_combo, values_combo, 0, 0, 0
values_boss: .long boss_locked, boss_open
values_combo: .long combo_normal, combo_full
entry_values: .long entry_value         ! Options row 8's value (MM.BIN literal)

! ---- strings: x, y in 8-pixel cells, then text (labels end at column 19,
! ---- values start at column 22, as on OPTION MODE)
title: .byte 9, 3, 1
        .asciz "EXTRA OPTIONS"
title_alt: .byte 9, 3, 100
        .asciz "EXTRA OPTIONS"
label_boss: .byte 6, 6
        .asciz "    BOSS FIGHT "
label_combo: .byte 6, 8
        .asciz "   COMBO GAUGE "
boss_locked: .byte 22, 6
        .asciz "LOCKED  "
boss_open: .byte 22, 6
        .asciz "UNLOCKED"
combo_normal: .byte 22, 8
        .asciz "NORMAL"
combo_full: .byte 22, 8
        .asciz "FULL  "
entry_value: .byte 22, 22
        .asciz "PRESS A OR C BUTTON"
        .align 4
end:
