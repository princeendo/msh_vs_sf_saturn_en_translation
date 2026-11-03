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
! ROWS (2, 3 or 4: BOSS FIGHT, COMBO GAUGE, NAMES, GRAMMAR FIXES) is given
! by the build (options_submenu).
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
        .equ SAVED, 0x06017ADC          ! P1 button struct +4: saved, never read (OPT-006)
        .equ MARK, 0x4E530000           ! NS in its upper half marks our value
        .equ SLOTS, 4
        .equ VBLANK_NEXT, 0x0600CB5C    ! what the V-blank handler called (SYS.BIN)

! ---- every frame, from the main V-blank-in handler (0x0600C13C), through
! ---- the guard in MM.BIN (0x0601E232), which checks this routine's first
! ---- long. The handler saved every register and pushed PR; VBLANK_NEXT
! ---- pops it and returns.
        .align 4
vblank:
        ! keep `switches` in SAVED, so BACK UP saves it. A marked value we did
        ! not write was loaded from the save: take it. Anything else (the
        ! Options screen writes a pointer there on entry) is overwritten.
        mov.l @(l_saved),r1
        mov.l @r1,r0
        mov.l @(l_last_saved),r2
        mov.l @r2,r3
        cmp/eq r0,r3
        bt save_switches
        mov r0,r4
        shlr16 r4
        shll16 r4
        mov.l @(l_mark),r5
        cmp/eq r4,r5
        bf save_switches
        mov #3,r4
        and r4,r0
        mov.l @(l_switches),r4
        mov.l r0,@r4
save_switches:
        mov.l @(l_switches),r4
        mov.l @r4,r12
        mov #3,r0
        and r0,r12                      ! bit 0 NAMES SATURN, bit 1 GRAMMAR FIXES ON
        mov.l @(l_mark),r0
        or r12,r0
        mov.l r0,@r1
        mov.l r0,@r2
        mov.l @(l_sites),r13
next_site:                              ! OPT-005 site table (names_switch.pack)
        mov.l @r13,r7                   ! address, or the offset in each slot
        tst r7,r7
        bt vblank_done
        mov.w @(4,r13),r0
        extu.w r0,r11                   ! length (even, >= 4)
        mov.w @(6,r13),r0
        extu.w r0,r6                    ! 1: in each character slot
        mov.w @(8,r13),r0
        extu.w r0,r10                   ! probe offset
        mov r13,r9
        add #12,r9                      ! r9 = the bytes to put there
        mov r9,r8
        add r11,r8                      ! r8 = the bytes to replace
        mov.w @(10,r13),r0              ! the site's setting bit
        and r12,r0
        tst r0,r0
        bt bytes_chosen                 ! bit clear: the disc's bytes over the other
        mov r9,r0
        mov r8,r9
        mov r0,r8
bytes_chosen:
        mov #1,r5
        tst r6,r6
        bt check_next
        mov #SLOTS,r5
        mov.l @(l_slot0),r0
        add r0,r7
check_next:
        bsr check_site
        sts.l pr,@-r15
        mov.l @(l_slot_step),r0
        add r0,r7
        dt r5
        bf check_next
        mov r11,r0                      ! next: 12 + 2 x length, rounded to 4
        shll r0
        add #15,r0
        shlr2 r0
        shll2 r0
        add r0,r13
        bra next_site
        nop
vblank_done:
        mov.l @(l_frames),r1
        mov.l @r1,r0
        add #1,r0
        mov.l r0,@r1
        mov.l @(l_vblank_next),r0
        jmp @r0
        nop

! r7 = address, r8 = bytes to replace, r9 = bytes to put, r10 = probe, r11 =
! length. Reads go through the cache-through alias. The copy writes both
! aliases: a store through the cached alias did not reach sound RAM
! (EXP-0112), and the cached store keeps any cached copy of work RAM
! current. Words only: sites are even.
check_site:
        mov.l @(l_uncached),r1
        or r7,r1
        mov r1,r2
        add r10,r2
        mov r8,r3
        add r10,r3
        mov #2,r4
probe_word:
        mov.w @r2+,r0
        mov.w @r3+,r6
        cmp/eq r0,r6
        bf site_done
        dt r4
        bf probe_word
        mov r1,r2
        mov r8,r3
        mov r11,r4
        shlr r4
full_word:
        mov.w @r2+,r0
        mov.w @r3+,r6
        cmp/eq r0,r6
        bf site_done
        dt r4
        bf full_word
        mov r7,r2
        mov r1,r6                       ! the cache-through alias
        mov r9,r3
        mov r11,r4
        shlr r4
copy_word:
        mov.w @r3+,r0
        mov.w r0,@r6
        mov.w r0,@r2
        add #2,r6
        dt r4
        bf/s copy_word
        add #2,r2
site_done:
        lds.l @r15+,pr
        rts
        nop

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
        mov.l @(20,r9),r0               ! a bit row toggles its bit
        tst r0,r0
        bt whole_value
        xor r0,r2
        bra change_store
        nop
whole_value:
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
        mov.l @(20,r9),r0               ! a bit row shows its bit as 0 or 1
        tst r0,r0
        bt value_ready
        mov.l @r8,r1
        and r1,r0
        tst r0,r0
        movt r0
        xor #1,r0
        mov.l @(l_bit_value),r8
        mov.l r0,@r8
value_ready:
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
l_frames: .long frames
l_saved: .long SAVED
l_last_saved: .long last_saved
l_mark: .long MARK
l_switches: .long switches
l_bit_value: .long bit_value
l_sites: .long sites
l_slot0: .long 0x00200000             ! character PAC slots (OPT-005)
l_slot_step: .long 0x00010000
l_uncached: .long 0x20000000
l_vblank_next: .long VBLANK_NEXT

! ---- variables (cart RAM is writable)
cursor: .long 0
row: .long 0
dir_bits: .long 0
frames: .long 0                         ! V-blank calls (EXP-0111)
bit_value: .long 0                      ! a bit row's value, for drawing
switches: .long 0                       ! NAMES (bit 0), GRAMMAR FIXES (bit 1)
last_saved: .long 0                     ! what vblank last wrote to SAVED

! ---- rows: setting, maximum, apply routine (0 = none), label, value strings,
! ---- bit (0 = the whole long; else the row toggles that bit)
rows:
        ! BOSS FIGHT: the title menu's boss fight unlock (OPT-001, EXP-0075)
        .long 0x06017AB0, 1, 0, label_boss, values_boss, 0, 0, 0
        ! COMBO GAUGE: the game's COMBO GAGE setting; 0x0601E172 applies it
        .long 0x06017AD4, 1, 0x0601E172, label_combo, values_combo, 0, 0, 0
        ! NAMES: American or Saturn names, applied every frame by `vblank`
        .long switches, 1, 0, label_names, values_names, 1, 0, 0
        ! GRAMMAR FIXES: TXT-004's corrections, applied every frame by `vblank`
        .long switches, 1, 0, label_grammar, values_grammar, 2, 0, 0
values_boss: .long boss_locked, boss_open
values_combo: .long combo_normal, combo_full
values_names: .long names_american, names_saturn
values_grammar: .long grammar_off, grammar_on
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
label_grammar: .byte 6, 12
        .asciz " GRAMMAR FIXES "
grammar_off: .byte 22, 12
        .asciz "OFF"
grammar_on: .byte 22, 12
        .asciz "ON "
label_names: .byte 6, 10
        .asciz "         NAMES "
names_american: .byte 22, 10
        .asciz "AMERICAN"
names_saturn: .byte 22, 10
        .asciz "SATURN  "
entry_value: .byte 22, 22
        .asciz "PRESS A OR C BUTTON"
        .align 4
end:
! ---- the OPT-005 site table goes here (names_switch.pack); empty: one zero
sites:  .long 0
