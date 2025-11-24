target b3 and b2 and b1 and b0;

transition inc0() not b0 {
    b0;
}
transition inc1() not b1 and b0 {
    b1; not b0;
}
transition inc2() not b2 and b1 and b0 {
    b2; not b1; not b0;
}
transition inc3() not b3 and b2 and b1 and b0 {
    b3; not b2; not b1; not b0;
}