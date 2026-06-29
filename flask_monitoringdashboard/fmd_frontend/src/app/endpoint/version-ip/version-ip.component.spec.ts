import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VersionIpComponent } from './version-ip.component';

describe('VersionIpComponent', () => {
  let component: VersionIpComponent;
  let fixture: ComponentFixture<VersionIpComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VersionIpComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VersionIpComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
