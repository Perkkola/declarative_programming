sourceformula p1 and (not p2) and (not p3) and (not p4) and not (p5);
target p5 and X and Y;

transition check_x_y_one() X and Y and p1 {
    not p1; p5;
}

transition check_x_y_zero() (not X) or (not Y) and p1 {
    not p1; p2;
}

transition check_x_zero() (not X) and p2 {
    not p2; p3;
}

transition check_x_one() X and p2 {
    not p2; p4;
}

transition set_x() p3 {
    X; p1; not p3;
}


transition set_y() p4 {
    Y; p1; not p4;
}
