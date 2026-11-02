! EXP-0108: an Options row handler in cart RAM that counts its calls.
! The caller pushed PR in the jsr delay slot (0x0601DF86), so pop it here.
        .equ COUNTER, 0x060FA000
start:
        mov.l @(counter),r1
        mov.l @r1,r0
        add #1,r0
        mov.l r0,@r1
        lds.l @r15+,pr
        rts
        nop
        .align 4
counter: .long COUNTER
